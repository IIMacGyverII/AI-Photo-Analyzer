"""Logging configuration for Ollama Image Analyzer."""

import logging
import sys
from pathlib import Path
from typing import Optional

from platformdirs import user_log_dir

from ollama_image_analyzer import PACKAGE_NAME


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True,
) -> None:
    """
    Configure application logging.

    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional path to log file. If None, uses default location.
        console: Whether to also log to console.
    """
    # Create logger
    logger = logging.getLogger("ollama_image_analyzer")
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file is not None or level <= logging.DEBUG:
        if log_file is None:
            log_dir = Path(user_log_dir(PACKAGE_NAME))
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "ollama_image_analyzer.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Logging initialized at {logging.getLevelName(level)} level")
    if log_file:
        logger.info(f"Log file: {log_file}")
