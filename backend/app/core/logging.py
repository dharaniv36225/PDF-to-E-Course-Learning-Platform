"""Structured application logging configuration."""
from __future__ import annotations

import logging
import sys
from logging.config import dictConfig

from app.core.config import settings


def configure_logging() -> None:
    """Configure root logging for the application."""
    log_level = settings.LOG_LEVEL.upper()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                },
            },
            "root": {"handlers": ["console"], "level": log_level},
            "loggers": {
                "uvicorn": {"handlers": ["console"], "level": log_level, "propagate": False},
                "uvicorn.error": {"handlers": ["console"], "level": log_level, "propagate": False},
                "uvicorn.access": {"handlers": ["console"], "level": log_level, "propagate": False},
                "sqlalchemy.engine": {"level": "WARNING"},
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)
