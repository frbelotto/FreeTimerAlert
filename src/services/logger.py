"""Logging service using Singleton pattern.

Provides centralized logging configuration as a single service for the entire application.
"""

from __future__ import annotations

import logging


class LoggerService:
    """Singleton service for centralized logging management.

    Ensures a single logging configuration exists throughout the application lifecycle.
    Each module can request its own named logger while sharing the same root configuration.
    """

    _instance: LoggerService | None = None

    def __new__(cls) -> LoggerService:
        """Implement Singleton pattern.

        Always returns the same instance, ensuring single logging service.

        Returns:
            The singleton LoggerService instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_root_logger()
        return cls._instance

    def _setup_root_logger(self) -> None:
        """Configure root logger for the application.

        Sets INFO level and simple console output formatting.
        """
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.handlers.clear()

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger instance.

        Args:
            name: Logger name (typically __name__ from calling module).

        Returns:
            Named Logger instance.
        """
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get logger from singleton service.

    Args:
        name: Logger name (typically __name__ from calling module).

    Returns:
        Named Logger instance from the singleton LoggerService.
    """
    service = LoggerService()  # Always returns the same instance
    return service.get_logger(name)
