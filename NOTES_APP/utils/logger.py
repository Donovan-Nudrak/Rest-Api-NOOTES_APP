#!/usr/bin/env python3
"""Rotating file logger under logs/api_activity.log for selected service-layer events."""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Mapping, Any


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGGER_NAME = "notes_app"
_LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")
_LOG_FILE = os.path.join(_PROJECT_ROOT, "logs", "api_activity.log")


def _ensure_log_dir() -> None:

    os.makedirs(_LOG_DIR, exist_ok=True)


def get_logger() -> logging.Logger:

    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    _ensure_log_dir()

    logger.setLevel(logging.INFO)


    handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_api_action(
    action: str,
    user_id: Optional[int] = None,
    status: str = "OK",
    extra: Optional[Mapping[str, Any]] = None,) -> None:

    logger = get_logger()

    parts = [f"action={action}", f"status={status}"]
    if user_id is not None:
        parts.append(f"user_id={user_id}")
    if extra:
        for key, value in extra.items():
            parts.append(f"{key}={value}")

    logger.info(" | ".join(parts))

