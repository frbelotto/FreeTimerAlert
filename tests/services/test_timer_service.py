"""Tests for timer_service module."""

from datetime import timedelta
import pytest
from src.services.timer_service import TimerService
from src.core.timer import TimerStatus


class TestTimerServiceBasics:
    """Basic timer service operations."""

    @pytest.fixture
    def service(self):
        """Create fresh timer service."""
        return TimerService()

    def test_create_timer(self, service):
        """Create timer adds it to catalog."""
        timer = service.create_timer("work", timedelta(minutes=25))

        assert timer is not None
        assert timer.duration == timedelta(minutes=25)
        assert "work" in service.list_timers()

    def test_create_duplicate_timer_raises(self, service):
        """Creating duplicate timer name raises ValueError."""
        service.create_timer("work", timedelta(minutes=25))

        with pytest.raises(ValueError, match="already exists"):
            service.create_timer("work", timedelta(minutes=10))

    def test_get_timer(self, service):
        """Get timer returns correct timer instance."""
        created = service.create_timer("test", timedelta(seconds=30))
        retrieved = service.get_timer("test")

        assert retrieved is created

    def test_get_nonexistent_timer(self, service):
        """Get nonexistent timer returns None."""
        assert service.get_timer("nonexistent") is None

    def test_list_timers_empty(self, service):
        """List timers on empty service returns empty dict."""
        assert service.list_timers() == {}

    def test_list_timers_multiple(self, service):
        """List timers returns all created timers."""
        service.create_timer("work", timedelta(minutes=25))
        service.create_timer("break", timedelta(minutes=5))

        timers = service.list_timers()
        assert len(timers) == 2
        assert "work" in timers
        assert "break" in timers


class TestTimerServiceOperations:
    """Timer control operations."""

    @pytest.fixture
    def service_with_timer(self):
        """Service with one timer."""
        service = TimerService()
        service.create_timer("test", timedelta(seconds=2))
        return service

    def test_start_timer(self, service_with_timer):
        """Start timer changes status to RUNNING."""
        service_with_timer.start_timer("test")
        timer = service_with_timer.get_timer("test")

        assert timer.status == TimerStatus.RUNNING
        timer.stop()

    def test_start_nonexistent_timer_raises(self, service_with_timer):
        """Start nonexistent timer raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            service_with_timer.start_timer("nonexistent")

    def test_pause_resume_timer(self, service_with_timer):
        """Pause and resume toggles timer state."""
        service_with_timer.start_timer("test")

        service_with_timer.pause_or_resume_timer("test")
        timer = service_with_timer.get_timer("test")
        assert timer.status == TimerStatus.PAUSED

        service_with_timer.pause_or_resume_timer("test")
        assert timer.status == TimerStatus.RUNNING

        timer.stop()

    def test_stop_timer(self, service_with_timer):
        """Stop timer changes status to STOPPED."""
        service_with_timer.start_timer("test")
        service_with_timer.stop_timer("test")

        timer = service_with_timer.get_timer("test")
        assert timer.status == TimerStatus.STOPPED

    def test_reset_timer(self, service_with_timer):
        """Reset timer restores original duration."""
        service_with_timer.start_timer("test")
        import time

        time.sleep(0.2)

        service_with_timer.reset_timer("test")
        timer = service_with_timer.get_timer("test")

        assert timer.status == TimerStatus.IDLE
        assert timer.remaining == timedelta(seconds=2)

    def test_add_time(self, service_with_timer):
        """Add time increases timer duration."""
        original = service_with_timer.get_timer("test").remaining
        service_with_timer.add_time("test", timedelta(seconds=5))

        timer = service_with_timer.get_timer("test")
        assert timer.remaining == original + timedelta(seconds=5)


class TestRemoveTimer:
    """Remove timer functionality."""

    @pytest.fixture
    def service(self):
        return TimerService()

    def test_remove_idle_timer(self, service):
        """Remove IDLE timer succeeds."""
        service.create_timer("test", timedelta(seconds=10))
        service.remove_timer("test")

        assert service.get_timer("test") is None

    def test_remove_stopped_timer(self, service):
        """Remove STOPPED timer succeeds."""
        service.create_timer("test", timedelta(seconds=10))
        service.start_timer("test")
        service.stop_timer("test")

        service.remove_timer("test")
        assert service.get_timer("test") is None

    def test_remove_running_timer_raises(self, service):
        """Remove RUNNING timer raises ValueError."""
        service.create_timer("test", timedelta(seconds=10))
        service.start_timer("test")

        with pytest.raises(ValueError, match="is still active"):
            service.remove_timer("test")

        service.stop_timer("test")

    def test_remove_nonexistent_timer_raises(self, service):
        """Remove nonexistent timer raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            service.remove_timer("nonexistent")
