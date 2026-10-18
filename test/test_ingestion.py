from __future__ import annotations

import logging
from io import StringIO

import pandas as pd

from src.ingestion.config import get_default_config
from src.ingestion.logging_config import BASE_LOGGER_NAME, DEFAULT_LOG_FILE, get_logger
from src.ingestion.pipeline import (
    acquire_market_data,
    run_full_pipeline,
    standardize_market_data,
)
from src.ingestion.validators import validate_standardized_frame


def test_default_config_lists_expected_instruments() -> None:
    config = get_default_config()
    assert config.instruments == ("NVDA", "AMD", "INTC", "TSM", "005930.KS")
    assert config.period == "5y"
    assert config.interval == "1d"


def test_standardize_market_data_maps_provider_columns() -> None:
    raw = pd.DataFrame(
        {
            ("NVDA", "Open"): [100.0, 101.0],
            ("NVDA", "High"): [110.0, 111.0],
            ("NVDA", "Low"): [99.0, 100.0],
            ("NVDA", "Close"): [105.0, 106.0],
            ("NVDA", "Adj Close"): [104.0, 105.0],
            ("NVDA", "Volume"): [10_000, 12_000],
            ("NVDA", "Dividends"): [0.0, 0.0],
            ("NVDA", "Stock Splits"): [0.0, 0.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    raw.columns = pd.MultiIndex.from_tuples(raw.columns, names=["Ticker", "Price"])

    standardized = standardize_market_data(raw, "NVDA")

    expected = [
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
    assert list(standardized.columns) == expected
    assert standardized["ticker"].tolist() == ["NVDA", "NVDA"]
    assert standardized["date"].dtype.kind == "M"


def test_standardize_market_data_maps_both_multiindex_orders() -> None:
    fields = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividends", "Stock Splits"]
    values = {
        "Open": [100.0],
        "High": [110.0],
        "Low": [99.0],
        "Close": [105.0],
        "Adj Close": [104.0],
        "Volume": [10_000],
        "Dividends": [0.0],
        "Stock Splits": [0.0],
    }
    dates = pd.to_datetime(["2024-01-02"])

    for level_order in ("ticker_first", "field_first"):
        column_tuples = [
            ("NVDA", field) if level_order == "ticker_first" else (field, "NVDA")
            for field in fields
        ]
        frame = pd.DataFrame(
            {column: values[field] for column, field in zip(column_tuples, fields)},
            index=dates,
        )
        frame.columns = pd.MultiIndex.from_tuples(frame.columns)

        standardized = standardize_market_data(frame, "NVDA")
        assert standardized.loc[0, ["open", "high", "low", "close", "adj_close", "volume"]].tolist() == [
            100.0,
            110.0,
            99.0,
            105.0,
            104.0,
            10_000,
        ]


def test_validation_rejects_duplicate_keys_and_negative_prices() -> None:
    bad = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-02"]),
            "ticker": ["NVDA", "NVDA"],
            "open": [100.0, 100.0],
            "high": [101.0, 90.0],
            "low": [99.0, 98.0],
            "close": [100.0, -1.0],
            "adj_close": [100.0, 100.0],
            "volume": [1000, -1],
            "dividends": [0.0, 0.0],
            "stock_splits": [0.0, 0.0],
        }
    )

    validation = validate_standardized_frame(bad)
    assert not validation.is_valid
    assert any("Duplicate" in finding for finding in validation.findings)
    assert any("Non-positive" in finding for finding in validation.findings)
    assert any("Negative volume" in finding for finding in validation.findings)
    assert any("High prices" in finding for finding in validation.findings)
    assert any("Low prices" in finding for finding in validation.findings)


def test_acquisition_uses_mocked_provider_download(monkeypatch) -> None:
    expected = pd.DataFrame({"Open": [1.0]})
    calls = []

    def fake_download(**kwargs):
        calls.append(kwargs)
        return expected

    monkeypatch.setattr("src.ingestion.pipeline.yf.download", fake_download)

    actual = acquire_market_data("NVDA", period="1mo", interval="1d")

    assert actual is expected
    assert calls[0]["tickers"] == "NVDA"
    assert calls[0]["period"] == "1mo"


def test_standardization_preserves_duplicate_dates_for_validation() -> None:
    frame = pd.DataFrame(
        {
            ("NVDA", "Open"): [100.0, 101.0],
            ("NVDA", "High"): [110.0, 111.0],
            ("NVDA", "Low"): [99.0, 100.0],
            ("NVDA", "Close"): [105.0, 106.0],
            ("NVDA", "Adj Close"): [104.0, 105.0],
            ("NVDA", "Volume"): [10_000, 12_000],
            ("NVDA", "Dividends"): [0.0, 0.0],
            ("NVDA", "Stock Splits"): [0.0, 0.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-02"]),
    )
    frame.columns = pd.MultiIndex.from_tuples(frame.columns)

    standardized = standardize_market_data(frame, "NVDA")
    outcome = validate_standardized_frame(standardized)

    assert len(standardized) == 2
    assert not outcome.is_valid
    assert any("Duplicate (date, ticker)" in finding for finding in outcome.findings)


def test_samsung_source_ohlc_anomaly_remains_a_strict_validation_failure() -> None:
    raw = pd.DataFrame(
        {
            ("005930.KS", "Open"): [59_500.0],
            ("005930.KS", "High"): [61_200.0],
            ("005930.KS", "Low"): [59_400.0],
            ("005930.KS", "Close"): [59_300.0],
            ("005930.KS", "Adj Close"): [57_472.359375],
            ("005930.KS", "Volume"): [20_886_249],
            ("005930.KS", "Dividends"): [0.0],
            ("005930.KS", "Stock Splits"): [0.0],
        },
        index=pd.to_datetime(["2024-10-14"]),
    )
    raw.columns = pd.MultiIndex.from_tuples(raw.columns, names=["Ticker", "Price"])

    standardized = standardize_market_data(raw, "005930.KS")
    outcome = validate_standardized_frame(standardized)

    assert standardized.loc[0, ["open", "high", "low", "close"]].tolist() == [
        59_500.0,
        61_200.0,
        59_400.0,
        59_300.0,
    ]
    assert not outcome.is_valid
    assert any("Low prices are above open or close" in finding for finding in outcome.findings)


def test_weekday_gap_is_reported_as_calendar_warning_not_validation_failure() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2021-12-30", "2022-01-04"]),
            "ticker": ["005930.KS", "005930.KS"],
            "open": [100.0, 101.0],
            "high": [110.0, 111.0],
            "low": [99.0, 100.0],
            "close": [105.0, 106.0],
            "adj_close": [104.0, 105.0],
            "volume": [10_000, 12_000],
            "dividends": [0.0, 0.0],
            "stock_splits": [0.0, 0.0],
        }
    )

    outcome = validate_standardized_frame(frame)

    assert outcome.is_valid
    assert outcome.findings == []
    assert len(outcome.warnings) == 1
    assert "2021-12-31" in outcome.warnings[0]
    assert "2022-01-03" in outcome.warnings[0]


def test_incomplete_run_does_not_overwrite_existing_combined_dataset(tmp_path, monkeypatch) -> None:
    from src.ingestion.config import PipelineConfig

    config = PipelineConfig(
        instruments=("NVDA", "AMD"),
        raw_data_dir=str(tmp_path / "raw"),
        processed_data_dir=str(tmp_path / "processed"),
    )
    config.processed_directory.mkdir(parents=True)
    output = config.processed_directory / config.combined_filename
    previous_content = "existing complete dataset\n"
    output.write_text(previous_content, encoding="utf-8")

    def fake_instrument(symbol, config):
        status = "accepted" if symbol == "NVDA" else "download_failed"
        result = {
            "instrument": symbol,
            "status": status,
            "accepted_observations": 1 if status == "accepted" else 0,
        }
        if status == "accepted":
            result["accepted_frame"] = pd.DataFrame(
                [["2024-01-02", "NVDA", 100, 110, 99, 105, 104, 1000, 0, 0]],
                columns=[
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
                ],
            )
        return result

    monkeypatch.setattr("src.ingestion.pipeline.run_instrument_pipeline", fake_instrument)

    report, _ = run_full_pipeline(config)

    assert report["overall_status"] == "partial_success"
    assert report["combined_output_write_status"] == "preserved_previous_output"
    assert output.read_text(encoding="utf-8") == previous_content


def test_logging_writes_timestamped_entries_and_tracebacks(tmp_path) -> None:
    log_file = tmp_path / "logs" / "ingestion.log"
    base_logger = logging.getLogger(BASE_LOGGER_NAME)
    console_handler = next(
        handler
        for handler in base_logger.handlers
        if getattr(handler, "_ingestion_handler_type", None) == "console"
    )
    previous_stream = console_handler.stream
    console_output = StringIO()
    try:
        console_handler.setStream(console_output)
        logger = get_logger("test_logging", log_file=log_file)
        logger.info("test event")
        try:
            raise ValueError("test traceback")
        except ValueError:
            logger.exception("test exception")

        file_output = log_file.read_text(encoding="utf-8")
        console_text = console_output.getvalue()

        assert "test event" in file_output
        assert "test exception" in file_output
        assert "Traceback (most recent call last)" in file_output
        assert "202" in file_output
        assert "test event" in console_text
        assert "test exception" in console_text
        assert "Traceback (most recent call last)" in console_text
    finally:
        console_handler.setStream(previous_stream)
        get_logger("test_restore_default", log_file=DEFAULT_LOG_FILE)


def test_logging_reuses_handlers_without_duplicates(tmp_path) -> None:
    log_file = tmp_path / "ingestion.log"
    get_logger("first_component", log_file=log_file)
    get_logger("second_component", log_file=log_file)

    base_logger = logging.getLogger(BASE_LOGGER_NAME)
    tagged_handlers = [
        handler
        for handler in base_logger.handlers
        if getattr(handler, "_ingestion_handler_type", None) in {"console", "file"}
    ]
    assert sum(getattr(handler, "_ingestion_handler_type", None) == "console" for handler in tagged_handlers) == 1
    assert sum(getattr(handler, "_ingestion_handler_type", None) == "file" for handler in tagged_handlers) == 1

    get_logger("restore_default", log_file=DEFAULT_LOG_FILE)
