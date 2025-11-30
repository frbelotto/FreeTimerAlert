"""Pytest fixtures for Timer tests.

Fixtures centralize common Timer setup patterns to keep individual tests
focused and concise. All docstrings in English; comments in Portuguese as per project requirements.
"""

from __future__ import annotations
from datetime import timedelta
import time
import pytest

from src.core.timer import Timer


@pytest.fixture
def timer_factory() -> callable:
    """Return a factory function that creates a Timer with given seconds.

    Simplifies timer creation with varying durations in tests.
    """

    def _create(seconds: float = 1.0) -> Timer:  # Factory simples
        return Timer(duration=timedelta(seconds=seconds))

    return _create


@pytest.fixture
def running_timer(timer_factory) -> Timer:
    """Return a started Timer and ensure proper stop after test.

    Duração curta para reduzir tempo total de execução do suite.
    """
    t = timer_factory(seconds=1.0)
    t.start()
    yield t
    # Garantia de limpeza do estado/thread
    if t.is_active:
        t.stop()


@pytest.fixture
def finished_timer(timer_factory) -> Timer:
    """Return a Timer that has already finished naturally.

    Useful for testing final states without waiting long periods.
    """
    t = timer_factory(seconds=0.6)  # Adjusted for 0.5s resolution
    t.start()
    time.sleep(1.5)  # Aguarda finalização com margem
    return t
