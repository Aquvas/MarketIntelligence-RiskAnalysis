from __future__ import annotations

import logging
from pathlib import Path

BASE_LOGGER_NAME = "market_intelligence.ingestion"
DEFAULT_LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "ingestion.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S%z"


def get_logger(
    component: str,
    *,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Return a component logger backed by shared console and file handlers."""

    target_file = Path(log_file) if log_file is not None else DEFAULT_LOG_FILE
    target_file = target_file.resolve()
    target_file.parent.mkdir(parents=True, exist_ok=True)

    base_logger = logging.getLogger(BASE_LOGGER_NAME)
    base_logger.setLevel(logging.DEBUG)
    base_logger.propagate = False

    has_console_handler = any(
        getattr(handler, "_ingestion_handler_type", None) == "console"
        for handler in base_logger.handlers
    )
    if not has_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        console_handler._ingestion_handler_type = "console"  # type: ignore[attr-defined]
        base_logger.addHandler(console_handler)

    file_handler = next(
        (
            handler
            for handler in base_logger.handlers
            if getattr(handler, "_ingestion_handler_type", None) == "file"
        ),
        None,
    )
    current_file = getattr(file_handler, "baseFilename", None)
    if file_handler is not None and Path(current_file).resolve() != target_file:
        base_logger.removeHandler(file_handler)
        file_handler.close()
        file_handler = None

    if file_handler is None:
        file_handler = logging.FileHandler(target_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        file_handler._ingestion_handler_type = "file"  # type: ignore[attr-defined]
        base_logger.addHandler(file_handler)

    component_logger = logging.getLogger(f"{BASE_LOGGER_NAME}.{component}")
    component_logger.setLevel(logging.NOTSET)
    component_logger.propagate = True
    return component_logger
