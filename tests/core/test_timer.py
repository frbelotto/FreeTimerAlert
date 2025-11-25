"""Core tests for `src.core.timer`.

Organized by functional areas with essential coverage only.
"""
from __future__ import annotations
import time
from datetime import timedelta
import pytest

from src.core.timer import Timer, TimerStatus


class TestTimerInitialization:
    """Timer creation and validation."""
    
    def test_valid_timer_starts_idle(self, timer_factory):
        """Timer initializes with correct duration and IDLE status."""
        t = timer_factory(seconds=2)
        assert t.duration == timedelta(seconds=2)
        assert t.remaining == t.duration
        assert t.status == TimerStatus.IDLE
        assert not t.running
    
    @pytest.mark.parametrize("invalid_seconds", [0, -5])
    def test_invalid_duration_rejected(self, invalid_seconds):
        """Zero or negative durations must raise ValueError."""
        with pytest.raises(ValueError, match="duration must be > 0"):
            Timer(duration=timedelta(seconds=invalid_seconds))


class TestTimerLifecycle:
    """Start, pause, resume, stop, and reset operations."""
    
    def test_start_activates_timer(self, running_timer):
        """Start transitions to RUNNING with active thread."""
        assert running_timer.status == TimerStatus.RUNNING
        assert running_timer.running
        assert running_timer.is_active
    
    def test_pause_resume_cycle(self, running_timer):
        """Pause/resume toggles RUNNING status correctly."""
        running_timer.pause()
        assert running_timer.status == TimerStatus.PAUSED
        assert not running_timer.running
        
        running_timer.resume()
        assert running_timer.status == TimerStatus.RUNNING
        assert running_timer.running
    
    def test_stop_deactivates_timer(self, running_timer):
        """Stop sets STOPPED status and ends thread."""
        running_timer.stop()
        assert running_timer.status == TimerStatus.STOPPED
        assert not running_timer.is_active
    
    def test_reset_restores_original_state(self, running_timer):
        """Reset returns to IDLE with full duration."""
        original = running_timer.duration
        time.sleep(0.2)
        running_timer.reset()
        assert running_timer.status == TimerStatus.IDLE
        assert running_timer.remaining == original
        assert not running_timer.is_active


class TestTimerTicking:
    """Time decrement and finish behavior."""
    
    @pytest.mark.parametrize("seconds", [1, 5])
    def test_tick_clamps_at_zero(self, seconds: int):
        """Tick sets FINISHED when time consumed."""
        t = Timer(duration=timedelta(seconds=1))
        t.status = TimerStatus.RUNNING
        t.tick(seconds=seconds)
        assert t.remaining == timedelta(0)
        assert t.status == TimerStatus.FINISHED
    
    @pytest.mark.parametrize("status", [TimerStatus.IDLE, TimerStatus.PAUSED])
    def test_tick_ignored_when_inactive(self, status):
        """Tick has no effect outside RUNNING state."""
        t = Timer(duration=timedelta(seconds=3))
        t.status = status
        before = t.remaining
        t.tick(seconds=1)
        assert t.remaining == before
    
    def test_thread_decrements_time(self, running_timer):
        """Background thread reduces remaining time."""
        first = running_timer.remaining
        time.sleep(0.3)
        assert running_timer.remaining < first
    
    def test_timer_finishes_naturally(self):
        """Timer reaches FINISHED when countdown completes."""
        t = Timer(duration=timedelta(seconds=0.3))
        t.start()
        time.sleep(0.5)
        assert t.status == TimerStatus.FINISHED
        assert not t.is_active


class TestTimerModification:
    """Add time and progress tracking."""
    
    def test_add_time_increases_remaining(self, timer_factory):
        """Adding time extends duration correctly."""
        t = timer_factory(seconds=3)
        t.add_time(timedelta(seconds=2))
        assert t.remaining == timedelta(seconds=5)
    
    def test_progress_advances_over_time(self, running_timer):
        """Progress fraction increases during execution."""
        p1 = running_timer.get_progress()
        time.sleep(0.25)
        p2 = running_timer.get_progress()
        assert p2 >= p1


class TestTimerCallbacks:
    """Event notification system."""
    
    def test_on_start_invoked(self, timer_factory):
        """on_start callbacks execute at start."""
        calls: list[int] = []
        
        t = timer_factory(0.5)
        t.on_start.append(lambda _: calls.append(1))
        t.on_start.append(lambda _: calls.append(2))
        t.start()
        time.sleep(0.1)
        t.stop()
        
        assert sorted(calls) == [1, 2]
    
    def test_on_end_invoked_on_finish(self):
        """on_end callbacks execute when timer completes."""
        executed: list[bool] = []
        
        t = Timer(duration=timedelta(seconds=0.3))
        t.on_end.append(lambda _: executed.append(True))
        t.start()
        time.sleep(0.5)
        
        assert executed
        assert t.status == TimerStatus.FINISHED
    
    def test_callback_exceptions_handled(self, timer_factory):
        """Exceptions in callbacks don't crash timer."""
        def bad_cb(timer: Timer) -> None:
            raise RuntimeError("boom")
        
        t = timer_factory(1)
        t.on_start.append(bad_cb)
        t.start()
        time.sleep(0.1)
        
        assert t.status == TimerStatus.RUNNING  # continues running
        t.stop()


class TestEdgeCases:
    """Boundary conditions and defensive behavior."""
    
    def test_operations_on_idle_timer_are_safe(self, timer_factory):
        """Pause/resume/stop on IDLE timer are no-ops."""
        t = timer_factory(1)
        t.pause()
        assert t.status == TimerStatus.IDLE
        
        t.resume()
        assert t.status == TimerStatus.IDLE
        
        t.stop()
        assert t.status == TimerStatus.IDLE
    
    def test_start_is_idempotent(self, timer_factory):
        """Calling start multiple times is safe."""
        t = timer_factory(1.0)
        t.start()
        time.sleep(0.05)
        t.start()  # second call does not cause error
        assert t.status == TimerStatus.RUNNING
        t.stop()

