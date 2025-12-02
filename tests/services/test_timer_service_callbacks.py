"""Tests for timer service callbacks."""

from datetime import timedelta
from unittest.mock import Mock
import pytest
from src.services.timer_service import TimerService
from src.core.timer import Timer


class TestTimerServiceCallbacks:
    """Test callback integration in TimerService."""

    @pytest.fixture
    def service(self):
        return TimerService()

    def test_create_timer_with_callbacks(self, service):
        """Create timer with callbacks attaches them correctly."""
        on_start = Mock()
        on_end = Mock()

        timer = service.create_timer("callback_test", timedelta(seconds=1), on_start=[on_start], on_end=[on_end])

        assert on_start in timer.on_start
        assert on_end in timer.on_end

        # Verify callbacks are executed
        timer.start()
        on_start.assert_called_once_with(timer)

        timer.stop()

    def test_create_timer_without_callbacks(self, service):
        """Create timer without callbacks initializes empty lists."""
        timer = service.create_timer("no_callback", timedelta(seconds=1))

        assert timer.on_start == []
        assert timer.on_end == []
