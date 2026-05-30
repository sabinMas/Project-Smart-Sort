"""Logging configuration for Box Smart Inbox."""

import logging
import json
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured JSON logging for the application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        timestamp=True,
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with structured logging.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """Helper class for structured logging with context."""

    def __init__(self, logger: logging.Logger):
        """Initialize with a logger instance."""
        self.logger = logger

    def info(self, message: str, **context: Any) -> None:
        """Log info message with context."""
        self.logger.info(message, extra={"context": context})

    def error(self, message: str, exception: Exception = None, **context: Any) -> None:
        """Log error message with context and optional exception."""
        extra = {"context": context}
        if exception:
            self.logger.error(message, exc_info=True, extra=extra)
        else:
            self.logger.error(message, extra=extra)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with context."""
        self.logger.warning(message, extra={"context": context})

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with context."""
        self.logger.debug(message, extra={"context": context})
