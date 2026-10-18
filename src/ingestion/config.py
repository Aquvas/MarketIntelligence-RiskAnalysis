from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class PipelineConfig:
    """Centralized configuration for the initial market-data ingestion pipeline."""

    instruments: Tuple[str, ...] = (
        "NVDA",
        "AMD",
        "INTC",
        "TSM",
        "005930.KS",
    )
    period: str = "5y"
    interval: str = "1d"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    combined_filename: str = "market_data.csv"
    run_report_filename: str = "run_report.json"
    project_version: str = "0.1.0"
    validation: dict[str, object] = field(
        default_factory=lambda: {
            "required_columns": [
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
            "numeric_columns": [
                "open",
                "high",
                "low",
                "close",
                "adj_close",
                "volume",
                "dividends",
                "stock_splits",
            ],
        }
    )

    @property
    def raw_directory(self) -> Path:
        return Path(self.raw_data_dir)

    @property
    def processed_directory(self) -> Path:
        return Path(self.processed_data_dir)


def get_default_config() -> PipelineConfig:
    """Return the default project configuration."""

    return PipelineConfig()
