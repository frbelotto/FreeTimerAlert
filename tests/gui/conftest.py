"""Pytest fixtures for GUI tests.

Provides common test fixtures for Tkinter GUI testing,
including mock windows and services.
"""

from __future__ import annotations

import tkinter as tk
from datetime import timedelta
from typing import Callable
from unittest.mock import Mock

import pytest

from src.services.timer_service import TimerService


@pytest.fixture
def tk_root() -> tk.Tk:
    """Create and cleanup Tkinter root window for testing.

    Ensures proper cleanup of Tkinter resources after each test.
    """
    root = tk.Tk()
    root.withdraw()  # Oculta janela durante testes
    yield root
    try:
        root.update_idletasks()
        root.destroy()
    except tk.TclError:
        pass  # Janela já foi destruída


@pytest.fixture
def timer_service() -> TimerService:
    """Create fresh timer service instance for testing."""
    return TimerService()


@pytest.fixture
def timer_service_with_timers() -> TimerService:
    """Create timer service with pre-populated timers.

    Returns service with three timers for testing list operations.
    """
    service = TimerService()
    service.create_timer("timer1", timedelta(minutes=25))
    service.create_timer("timer2", timedelta(minutes=5))
    service.create_timer("timer3", timedelta(seconds=30))
    return service


@pytest.fixture
def mock_timer_service() -> Mock:
    """Create mock timer service for isolated GUI testing.

    Useful for testing GUI components without actual timer logic.
    """
    mock_service = Mock(spec=TimerService)
    mock_service.list_timers.return_value = {}
    mock_service.get_timer.return_value = None
    return mock_service


@pytest.fixture
def mock_callback() -> Mock:
    """Create a mock callback function for testing callbacks."""
    return Mock()
