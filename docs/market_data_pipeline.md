# Market data ingestion pipeline

## Purpose
This pipeline collects daily market histories for the initial market-stress classification phase. It focuses on a small, configurable universe of equity instruments and preserves a clean, standardized dataset suitable for downstream feature engineering.

## Configuration
The default configuration is centralized in `src/ingestion/config.py`.

- Instruments: `NVDA`, `AMD`, `INTC`, `TSM`, `005930.KS`
- Period: `5y`
- Interval: `1d`
- Raw output directory: `data/raw`
- Processed output directory: `data/processed`

This keeps ticker additions and removals concentrated in one place rather than scattering instrument-specific logic across the pipeline.

## Acquisition and preservation
The acquisition step runs a single-symbol `yfinance.download()` call and returns the raw DataFrame only when it is non-empty. Failures are recorded as `download_failure` and are never silently treated as success.

Raw snapshots are saved under `data/raw` using a transparent naming convention:

- `{ticker}_{UTC_timestamp}.csv`
- `{ticker}_{UTC_timestamp}_metadata.json`

This preserves the provider response in a durable, unambiguous form without overwriting earlier snapshots. The metadata sidecar records the requested period, interval, timestamp, and software version. The raw CSV is preserved as a tabular result from the provider, not necessarily the original HTTP payload.

## Standardization
The standardization step converts all successful provider responses into a shared schema:

- `date`
- `ticker`
- `open`
- `high`
- `low`
- `close`
- `adj_close`
- `volume`
- `dividends`
- `stock_splits`

Provider-specific behavior is normalized explicitly. For single-symbol `yfinance` calls, a MultiIndex column layout is flattened before mapping to the common schema. The `adj_close` column is kept only when the provider returns it; the pipeline never fabricates it from `close`.

Dates are represented as Python/Pandas timestamps without timezone conversion so that the trading calendar remains aligned to the local market date rather than shifting into a different local day.

## Validation policy
The validation checks cover:

- required columns and schema
- duplicate `(date, ticker)` keys
- non-positive OHLC values
- negative volume
- OHLC consistency checks
- monotonic date ordering
- exchange-aware gap detection that does not confuse weekends and holidays with invalid missing data

The acceptance policy is explicit: a dataset is accepted only when it passes validation; incomplete or partially invalid data is reported instead of silently modified.

## Logging
The reusable logging setup is in `src/ingestion/logging_config.py`. Pipeline, downloader, and validator components use named child loggers with one shared console handler and one shared file handler, so repeated setup does not duplicate output handlers.

Logs are written to `logs/ingestion.log`; the directory is created automatically. Console output starts at `INFO`, while the file also retains `DEBUG` messages. Each record includes a timestamp, severity, component logger name, and message. Exceptions caught during acquisition or unexpected validation/persistence errors are logged with their traceback before the existing error handling continues or re-raises.

The `logs/` directory is ignored by Git because log output is generated locally and may contain provider error details.

## Listing-specific notes
The dataset starts with a US-listed ADR/stock set and a Korea Exchange listing (`005930.KS`). The instruments do not all share the same trading calendar, exchange hours, or price conventions.

### Unresolved Samsung data-quality exception

The Samsung provider history contains an unresolved OHLC inconsistency on **2024-10-14**: `open=59,500`, `high=61,200`, `low=59,400`, and `close=59,300`. The `low` exceeds the `close`, and the strict OHLC validator correctly rejects the instrument. The raw and standardized records agree, so the pipeline does not adjust, fabricate, or remove these values. Samsung remains `partial` with this finding in `data/processed/run_report.json` and is excluded from the accepted combined dataset and model-training inputs until the source record is investigated.

Weekday absences for `005930.KS` are reported as candidate-gap warnings pending KRX calendar verification; they are not treated as confirmed missing sessions. The four accepted instruments continue to be available for development. A partial run preserves the existing combined CSV rather than replacing it.
