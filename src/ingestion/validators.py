from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.ingestion.logging_config import get_logger

logger = get_logger("validators")

REQUIRED_COLUMNS = [
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

NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
    "dividends",
    "stock_splits",
]


@dataclass
class ValidationOutcome:
    is_valid: bool
    findings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    accepted_rows: int = 0


def _as_numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(pd.NA, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce")


def validate_standardized_frame(
    frame: pd.DataFrame,
    *,
    expected_start: pd.Timestamp | None = None,
    expected_end: pd.Timestamp | None = None,
) -> ValidationOutcome:
    """Validate that a standardized market-data frame meets the ingestion contract."""

    findings: list[str] = []
    if frame is None or frame.empty:
        finding = "Dataset is empty."
        logger.warning("Market data validation failed: %s", finding)
        return ValidationOutcome(is_valid=False, findings=[finding], accepted_rows=0)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        findings.append(f"Missing required columns: {missing_columns}.")

    normalized = frame.copy()
    if "date" in normalized.columns:
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
        if normalized["date"].isna().any():
            findings.append("Date column contains invalid timestamps.")

    if "ticker" in normalized.columns:
        normalized["ticker"] = normalized["ticker"].astype(str).str.strip()
        if normalized["ticker"].eq("").any():
            findings.append("Ticker column contains blank values.")

    if {"date", "ticker"}.issubset(normalized.columns):
        duplicates = normalized[["date", "ticker"]].duplicated().sum()
        if duplicates:
            findings.append(f"Duplicate (date, ticker) keys detected: {duplicates} row(s).")

    for column in NUMERIC_COLUMNS:
        if column in normalized.columns:
            numeric_values = _as_numeric(normalized, column)
            if column == "volume":
                negative_volume = numeric_values < 0
                if negative_volume.any():
                    findings.append(f"Negative volume values detected in '{column}'.")
            elif column in {"open", "high", "low", "close", "adj_close"}:
                non_positive = numeric_values.notna() & (numeric_values <= 0)
                if non_positive.any():
                    findings.append(f"Non-positive price values detected in '{column}'.")

    if {"open", "high", "low", "close"}.issubset(normalized.columns):
        open_values = _as_numeric(normalized, "open")
        high_values = _as_numeric(normalized, "high")
        low_values = _as_numeric(normalized, "low")
        close_values = _as_numeric(normalized, "close")
        invalid_high = (high_values.notna()) & ((high_values < open_values) | (high_values < close_values) | (high_values < low_values))
        invalid_low = (low_values.notna()) & ((low_values > open_values) | (low_values > close_values))
        if invalid_high.any():
            findings.append("High prices are below open, close, or low for at least one observation.")
        if invalid_low.any():
            findings.append("Low prices are above open or close for at least one observation.")

    candidate_missing_weekdays: set[str] = set()
    if {"date", "ticker"}.issubset(normalized.columns):
        for ticker_name, ticker_frame in normalized.groupby("ticker", sort=False):
            ordered = ticker_frame.sort_values("date").copy()
            if not ordered["date"].is_monotonic_increasing:
                findings.append(f"Date ordering is not monotonic for ticker {ticker_name}.")
            if len(ordered) > 1:
                gaps = ordered["date"].diff().dropna()
                if (gaps <= pd.Timedelta(0)).any():
                    findings.append(f"Duplicate or reverse dates observed for ticker {ticker_name}.")
                actual_dates = ordered["date"].dt.normalize().drop_duplicates().sort_values().reset_index(drop=True)
                for left, right in zip(actual_dates[:-1], actual_dates[1:]):
                    expected_business_window = pd.bdate_range(start=left, end=right)
                    if len(expected_business_window) > 2:
                        missing_in_window = expected_business_window[1:-1].difference(actual_dates)
                        candidate_missing_weekdays.update(
                            date.strftime("%Y-%m-%d") for date in missing_in_window
                        )

    warnings: list[str] = []
    if candidate_missing_weekdays:
        candidate_dates = ", ".join(sorted(candidate_missing_weekdays))
        warnings.append(
            "Weekday dates are absent between observations and need exchange-calendar verification "
            f"before being treated as missing trading sessions: {candidate_dates}."
        )

    if expected_start is not None or expected_end is not None:
        if "date" in normalized.columns:
            start = normalized["date"].min()
            end = normalized["date"].max()
            if expected_start is not None and pd.notna(start) and start > expected_start:
                findings.append(
                    f"Data coverage starts after the requested window: first available date {start.date()} > requested start {expected_start.date()}."
                )
            if expected_end is not None and pd.notna(end) and end < (expected_end - pd.Timedelta(days=1)):
                findings.append(
                    f"Data coverage ends before the requested window: last available date {end.date()} < requested end {expected_end.date()}."
                )

    if "adj_close" in normalized.columns:
        missing_adj_close = normalized["adj_close"].isna().all()
        if missing_adj_close:
            findings.append(
                "Adjusted close is completely missing; the pipeline does not fabricate a value from the close price."
            )

    valid = len(findings) == 0
    if valid:
        logger.debug("Market data validation passed for %d observations.", len(normalized))
    else:
        logger.warning("Market data validation failed: %s", "; ".join(findings))
    for warning in warnings:
        logger.warning("Market data validation warning: %s", warning)
    return ValidationOutcome(
        is_valid=valid,
        findings=findings,
        warnings=warnings,
        accepted_rows=len(normalized) if valid else 0,
    )
