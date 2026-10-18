from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import yfinance as yf

from src.ingestion.config import PipelineConfig, get_default_config
from src.ingestion.logging_config import get_logger
from src.ingestion.validators import REQUIRED_COLUMNS, validate_standardized_frame

logger = get_logger("pipeline")
downloader_logger = get_logger("downloader")

STANDARD_SCHEMA = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
    "dividends",
    "stock_splits",
]

PROVIDER_FIELD_NAMES = {
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "adjclose",
    "volume",
    "dividends",
    "stock_splits",
}


class DownloadFailure(RuntimeError):
    """Raised when the provider fails to return usable market data."""


class ValidationFailure(RuntimeError):
    """Raised when provider data is downloaded but fails the pipeline schema quality checks."""


def _ensure_directories(config: PipelineConfig) -> None:
    config.raw_directory.mkdir(parents=True, exist_ok=True)
    config.processed_directory.mkdir(parents=True, exist_ok=True)


def acquire_market_data(
    symbol: str,
    *,
    period: str = "5y",
    interval: str = "1d",
    config: PipelineConfig | None = None,
) -> pd.DataFrame:
    """Download a single instrument history from Yahoo Finance."""

    config = config or get_default_config()
    resolved_symbol = str(symbol).strip()
    if not resolved_symbol:
        downloader_logger.error("Cannot download market data for a blank instrument identifier.")
        raise DownloadFailure("Instrument identifier is blank.")

    downloader_logger.info(
        "Downloading market data for %s (period=%s, interval=%s).",
        resolved_symbol,
        period,
        interval,
    )
    try:
        result = yf.download(
            tickers=resolved_symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            actions=True,
            threads=False,
            group_by="ticker",
        )
    except Exception as exc:  # pragma: no cover - defensive branch
        downloader_logger.exception("yfinance download failed for %s.", resolved_symbol)
        raise DownloadFailure(f"yfinance download failed for {resolved_symbol}: {exc}") from exc

    if result is None or result.empty:
        downloader_logger.warning("yfinance returned no usable rows for %s.", resolved_symbol)
        raise DownloadFailure(f"yfinance returned no usable rows for {resolved_symbol}.")

    downloader_logger.info(
        "Downloaded %d observations for %s.",
        len(result),
        resolved_symbol,
    )
    return result


def standardize_market_data(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Normalize a provider response to the pipeline's common market-data schema."""

    if frame is None or frame.empty:
        raise ValidationFailure("Downloaded history frame is empty and cannot be standardized.")

    working = frame.copy()
    if isinstance(working.columns, pd.MultiIndex):
        field_columns: list[str] = []
        for column in working.columns:
            normalized_levels = [
                str(level).strip().lower().replace(" ", "_").replace("-", "_")
                for level in column
            ]
            provider_fields = [level for level in normalized_levels if level in PROVIDER_FIELD_NAMES]
            if len(provider_fields) != 1:
                raise ValidationFailure(
                    f"Could not identify exactly one provider field in MultiIndex column {column!r}."
                )
            field_columns.append(provider_fields[0])
        working.columns = field_columns
    else:
        working.columns = [
            str(column).strip().lower().replace(" ", "_").replace("-", "_") for column in working.columns
        ]

    duplicate_columns = working.columns[working.columns.duplicated()].tolist()
    if duplicate_columns:
        raise ValidationFailure(
            "Duplicate provider fields after column normalization: "
            + ", ".join(str(column) for column in duplicate_columns)
            + "."
        )

    if "date" not in working.columns and isinstance(working.index, pd.DatetimeIndex):
        working = working.rename_axis("date").reset_index()

    if "date" not in working.columns and not isinstance(working.index, pd.DatetimeIndex):
        raise ValidationFailure("Downloaded history is missing a usable date column or Datetime index.")

    if "date" in working.columns:
        working["date"] = pd.to_datetime(working["date"], errors="coerce")
        if working["date"].isna().any():
            raise ValidationFailure("Downloaded history contains invalid dates and cannot be standardized.")
        if isinstance(working["date"].dtype, pd.DatetimeTZDtype):
            working["date"] = working["date"].dt.tz_localize(None)

    rename_map = {
        "adjclose": "adj_close",
        "adj_close": "adj_close",
        "close": "close",
        "open": "open",
        "high": "high",
        "low": "low",
        "volume": "volume",
        "dividends": "dividends",
        "stock_splits": "stock_splits",
        "date": "date",
    }

    for source_name, target_name in rename_map.items():
        if source_name in working.columns:
            working = working.rename(columns={source_name: target_name})

    if "adj_close" not in working.columns:
        working["adj_close"] = pd.NA

    working["ticker"] = str(symbol).strip()

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in working.columns]
    if missing_columns:
        raise ValidationFailure(
            "Missing required columns after standardization: " + ", ".join(missing_columns) + "."
        )

    standardized = working.loc[:, STANDARD_SCHEMA].copy()
    standardized = standardized.sort_values(["ticker", "date"]).reset_index(drop=True)
    return standardized


def _save_raw_snapshot(raw_frame: pd.DataFrame, symbol: str, config: PipelineConfig) -> tuple[str, str]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_symbol = str(symbol).strip().replace(" ", "_")
    raw_path = config.raw_directory / f"{safe_symbol}_{timestamp}.csv"
    raw_frame.to_csv(raw_path, index=True)

    metadata = {
        "ticker": safe_symbol,
        "period": config.period,
        "interval": config.interval,
        "retrieval_timestamp_utc": timestamp,
        "client_settings": {
            "auto_adjust": False,
            "group_by": "ticker",
        },
        "software_version": config.project_version,
        "dataset_note": "Raw CSV preserves the returned market table as returned by yfinance; it is not guaranteed to be the original HTTP payload.",
    }
    metadata_path = config.raw_directory / f"{safe_symbol}_{timestamp}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return str(raw_path), str(metadata_path)


def run_instrument_pipeline(
    symbol: str,
    config: PipelineConfig | None = None,
) -> dict[str, Any]:
    """Acquire, preserve, standardize, validate, and report one instrument."""

    config = config or get_default_config()
    _ensure_directories(config)

    retrieval_timestamp = datetime.now(timezone.utc).isoformat()
    report: dict[str, Any] = {
        "instrument": str(symbol).strip(),
        "status": "download_failed",
        "downloaded_observations": 0,
        "accepted_observations": 0,
        "first_available_date": None,
        "last_available_date": None,
        "validation_findings": [],
        "validation_warnings": [],
        "error_category": None,
        "error_message": None,
        "retrieval_timestamp": retrieval_timestamp,
    }

    try:
        raw_frame = acquire_market_data(
            symbol,
            period=config.period,
            interval=config.interval,
            config=config,
        )
    except DownloadFailure as exc:
        report["error_category"] = "download_failure"
        report["error_message"] = str(exc)
        logger.warning("Instrument %s download failed: %s", symbol, exc)
        return report

    report["downloaded_observations"] = len(raw_frame)
    try:
        raw_snapshot_path, metadata_path = _save_raw_snapshot(raw_frame, symbol, config)
    except Exception:
        logger.exception("Could not preserve the raw snapshot for %s.", symbol)
        raise
    report["raw_snapshot_path"] = raw_snapshot_path
    report["raw_metadata_path"] = metadata_path
    logger.info(
        "Preserved %d raw observations for %s at %s.",
        len(raw_frame),
        symbol,
        raw_snapshot_path,
    )

    try:
        standardized = standardize_market_data(raw_frame, symbol)
    except ValidationFailure as exc:
        report["status"] = "validation_failed"
        report["error_category"] = "validation_failure"
        report["error_message"] = str(exc)
        report["validation_findings"] = [str(exc)]
        logger.warning("Instrument %s failed standardization: %s", symbol, exc)
        return report

    current_time = pd.Timestamp.now(tz="UTC").tz_localize(None)
    expected_end = current_time - pd.Timedelta(days=1)
    try:
        validation_outcome = validate_standardized_frame(
            standardized,
            expected_start=current_time - pd.DateOffset(years=5),
            expected_end=expected_end,
        )
    except Exception:
        logger.exception("Unexpected validation error for %s.", symbol)
        raise
    report["validation_findings"] = validation_outcome.findings
    report["validation_warnings"] = validation_outcome.warnings

    if not standardized.empty:
        report["first_available_date"] = standardized["date"].min().isoformat()
        report["last_available_date"] = standardized["date"].max().isoformat()

    if validation_outcome.is_valid:
        report["status"] = "accepted"
        report["accepted_observations"] = len(standardized)
        report["error_category"] = None
        report["error_message"] = None
        report["accepted_frame"] = standardized
        logger.info(
            "Accepted %d observations for %s.",
            len(standardized),
            symbol,
        )
        return report

    report["status"] = "partial" if len(standardized) > 0 else "validation_failed"
    report["error_category"] = "validation_failure"
    report["error_message"] = "; ".join(validation_outcome.findings)
    report["accepted_frame"] = standardized
    logger.warning(
        "Instrument %s has status %s with validation findings: %s",
        symbol,
        report["status"],
        report["error_message"],
    )
    return report


def run_full_pipeline(config: PipelineConfig | None = None) -> tuple[dict[str, Any], pd.DataFrame]:
    """Run the configured set of instruments and rebuild the combined processed dataset."""

    config = config or get_default_config()
    _ensure_directories(config)
    logger.info("Starting ingestion run for %d configured instruments.", len(config.instruments))

    combined_frames: list[pd.DataFrame] = []
    run_reports: list[dict[str, Any]] = []

    for symbol in config.instruments:
        report = run_instrument_pipeline(symbol, config=config)
        run_reports.append(report)
        if report.get("status") == "accepted":
            combined_frames.append(report["accepted_frame"])

    combined = pd.concat(combined_frames, ignore_index=True) if combined_frames else pd.DataFrame(columns=STANDARD_SCHEMA)
    if not combined.empty:
        combined = combined.drop_duplicates(subset=["date", "ticker"]).sort_values(["ticker", "date"]).reset_index(drop=True)
        combined = combined.loc[:, STANDARD_SCHEMA]

    if all(report.get("status") == "accepted" for report in run_reports):
        overall_status = "success"
    elif any(report.get("status") == "accepted" for report in run_reports):
        overall_status = "partial_success"
    else:
        overall_status = "failed"

    output_path = config.processed_directory / config.combined_filename
    if overall_status == "success" or not output_path.exists():
        combined.to_csv(output_path, index=False, mode="w")
        output_write_status = "written"
    else:
        output_write_status = "preserved_previous_output"
        logger.warning(
            "Preserving existing combined dataset at %s because ingestion status is %s.",
            output_path,
            overall_status,
        )

    run_report = {
        "overall_status": overall_status,
        "instrument_reports": run_reports,
        "combined_output": str(output_path),
        "combined_output_write_status": output_write_status,
        "accepted_instruments": sum(1 for report in run_reports if report.get("status") == "accepted"),
        "required_instruments": len(config.instruments),
    }

    run_report_path = config.processed_directory / config.run_report_filename
    run_report_path.write_text(json.dumps(run_report, indent=2, default=str), encoding="utf-8")
    logger.info(
        "Ingestion run finished with status %s: accepted %d of %d instruments; processed output=%s.",
        overall_status,
        run_report["accepted_instruments"],
        run_report["required_instruments"],
        output_path,
    )
    return run_report, combined


if __name__ == "__main__":
    run_full_pipeline()
