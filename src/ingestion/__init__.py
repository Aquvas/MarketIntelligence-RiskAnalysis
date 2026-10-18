"""Ingestion package for market data acquisition and validation."""

from .config import PipelineConfig, get_default_config
from .pipeline import (
    DownloadFailure,
    ValidationFailure,
    acquire_market_data,
    run_full_pipeline,
    run_instrument_pipeline,
    standardize_market_data,
)
from .validators import ValidationOutcome, validate_standardized_frame

__all__ = [
    "PipelineConfig",
    "DownloadFailure",
    "ValidationFailure",
    "ValidationOutcome",
    "acquire_market_data",
    "get_default_config",
    "run_full_pipeline",
    "run_instrument_pipeline",
    "standardize_market_data",
    "validate_standardized_frame",
]
