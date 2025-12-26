"""Integration tests for FreeTimer application.

Tests complete workflows involving multiple components working together.
These tests verify that different parts of the system integrate correctly.
"""

import time
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.timer import Timer, TimerStatus
from src.interfaces.terminal.notifications import get_sound_path
from src.services.parse_utils import parse_time
from src.services.timer_service import TimerService


@pytest.mark.integration
class TestTimerServiceIntegration:
    """Integration tests for TimerService with Timer."""

    def test_complete_timer_lifecycle_with_service(self):
        """Test complete timer lifecycle through TimerService."""
        service = TimerService()
        
        # Create timer through service
        timer = service.create_timer("integration_test", timedelta(seconds=2))
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining == timedelta(seconds=2)
        
        # Start timer
        service.start_timer("integration_test")
        assert timer.status == TimerStatus.RUNNING
        
        # Pause timer
        service.pause_or_resume_timer("integration_test")
        assert timer.status == TimerStatus.PAUSED
        remaining_after_pause = timer.remaining
        
        # Resume timer
        service.pause_or_resume_timer("integration_test")
        assert timer.status == TimerStatus.RUNNING
        
        # Wait for completion
        time.sleep(2.5)
        assert timer.status == TimerStatus.FINISHED
        assert timer.remaining == timedelta(0)
        
        # Reset timer
        service.reset_timer("integration_test")
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining == timedelta(seconds=2)
        
        # Remove timer
        service.remove_timer("integration_test")
        assert service.get_timer("integration_test") is None

    def test_multiple_timers_concurrent_execution(self):
        """Test multiple timers running simultaneously."""
        service = TimerService()
        
        # Create multiple timers
        timer1 = service.create_timer("timer1", timedelta(seconds=1))
        timer2 = service.create_timer("timer2", timedelta(seconds=2))
        timer3 = service.create_timer("timer3", timedelta(seconds=3))
        
        # Start all timers
        service.start_timer("timer1")
        service.start_timer("timer2")
        service.start_timer("timer3")
        
        assert timer1.status == TimerStatus.RUNNING
        assert timer2.status == TimerStatus.RUNNING
        assert timer3.status == TimerStatus.RUNNING
        
        # Wait for first timer to finish
        time.sleep(1.5)
        assert timer1.status == TimerStatus.FINISHED
        assert timer2.status == TimerStatus.RUNNING
        assert timer3.status == TimerStatus.RUNNING
        
        # Wait for second timer to finish
        time.sleep(1)
        assert timer1.status == TimerStatus.FINISHED
        assert timer2.status == TimerStatus.FINISHED
        assert timer3.status == TimerStatus.RUNNING
        
        # Stop third timer before it finishes
        service.stop_timer("timer3")
        assert timer3.status == TimerStatus.STOPPED


@pytest.mark.integration
class TestTimerWithCallbacks:
    """Integration tests for Timer with callbacks."""

    def test_timer_callbacks_integration(self):
        """Test timer callbacks are triggered correctly during lifecycle."""
        on_start_called = []
        on_end_called = []
        
        def on_start_callback(timer):
            on_start_called.append(time.time())
        
        def on_end_callback(timer):
            on_end_called.append(time.time())
        
        # Create timer with callbacks
        timer = Timer(
            duration=timedelta(seconds=1),
            on_start=[on_start_callback],
            on_end=[on_end_callback]
        )
        
        # Start timer
        start_time = time.time()
        timer.start()
        
        # Verify on_start was called
        time.sleep(0.1)
        assert len(on_start_called) == 1
        assert on_start_called[0] >= start_time
        
        # Wait for timer to finish
        time.sleep(1.5)
        assert timer.status == TimerStatus.FINISHED
        
        # Verify on_end was called
        assert len(on_end_called) == 1
        assert on_end_called[0] > on_start_called[0]
        assert on_end_called[0] - on_start_called[0] >= 1.0

    def test_timer_service_with_callbacks(self):
        """Test TimerService properly passes callbacks to Timer."""
        service = TimerService()
        callback_data = {"start_count": 0, "end_count": 0}
        
        def on_start(timer):
            callback_data["start_count"] += 1
        
        def on_end(timer):
            callback_data["end_count"] += 1
        
        # Create timer with callbacks through service
        timer = service.create_timer(
            "callback_timer",
            timedelta(seconds=1),
            on_start=[on_start],
            on_end=[on_end]
        )
        
        # Start and wait for completion
        service.start_timer("callback_timer")
        time.sleep(1.5)
        
        # Verify callbacks were triggered
        assert callback_data["start_count"] == 1
        assert callback_data["end_count"] == 1


@pytest.mark.integration
class TestParseUtilsIntegration:
    """Integration tests for parse_utils with Timer."""

    def test_parse_time_creates_valid_timer(self):
        """Test that parsed time creates valid timers."""
        test_cases = [
            ("30", timedelta(seconds=30)),
            ("5m", timedelta(minutes=5)),
            ("1h", timedelta(hours=1)),
            ("1h30m", timedelta(hours=1, minutes=30)),
            ("2h15m30s", timedelta(hours=2, minutes=15, seconds=30)),
        ]
        
        for time_str, expected_duration in test_cases:
            duration = parse_time(time_str)
            assert duration == expected_duration
            
            # Verify timer can be created with parsed duration
            timer = Timer(duration=duration)
            assert timer.duration == expected_duration
            assert timer.remaining == expected_duration

    def test_parse_time_with_timer_service(self):
        """Test parse_time integration with TimerService."""
        service = TimerService()
        
        # Parse and create timer
        duration_str = "2m30s"
        duration = parse_time(duration_str)
        timer = service.create_timer("parsed_timer", duration)
        
        assert timer.duration == timedelta(minutes=2, seconds=30)
        assert timer.duration.total_seconds() == 150


@pytest.mark.integration
class TestNotificationsIntegration:
    """Integration tests for notification system."""

    @patch("playsound3.playsound")
    def test_sound_paths_are_valid(self, mock_playsound):
        """Test that sound file paths resolve correctly."""
        from src.interfaces.terminal.notifications import play_start_sound, play_end_sound
        
        # Verify sound files exist
        start_sound = get_sound_path("clock-start.mp3")
        end_sound = get_sound_path("timer-terminer.mp3")
        
        assert start_sound.exists(), f"Start sound not found: {start_sound}"
        assert end_sound.exists(), f"End sound not found: {end_sound}"
        
        # Test playing sounds
        play_start_sound()
        play_end_sound()
        
        # Verify playsound was called
        assert mock_playsound.call_count == 2

    @patch("src.services.system_notifications.show_notification")
    @patch("src.interfaces.terminal.notifications.play_end_sound")
    def test_timer_notifications_integration(self, mock_sound, mock_notification):
        """Test timer completion triggers both sound and system notifications."""
        notification_triggered = []
        
        def track_notification(timer):
            from src.services.system_notifications import show_timer_finished_notification
            show_timer_finished_notification("test_timer")
            notification_triggered.append(True)
        
        # Create timer with notification callback
        timer = Timer(
            duration=timedelta(seconds=1),
            on_end=[track_notification]
        )
        
        # Start timer and wait for completion
        timer.start()
        time.sleep(1.5)
        
        assert timer.status == TimerStatus.FINISHED
        assert len(notification_triggered) == 1
        
        # Verify system notification was called
        mock_notification.assert_called_once()
        call_args = mock_notification.call_args
        assert "test_timer" in str(call_args)


@pytest.mark.integration
class TestCompleteUserWorkflow:
    """Integration tests simulating complete user workflows."""

    @patch("playsound3.playsound")
    def test_complete_terminal_workflow(self, mock_playsound):
        """Test complete workflow: create, start, pause, resume, finish."""
        service = TimerService()
        workflow_events = []
        
        def on_start(timer):
            workflow_events.append("started")
        
        def on_end(timer):
            workflow_events.append("finished")
        
        # 1. Parse time from user input
        duration = parse_time("2s")
        
        # 2. Create timer
        timer = service.create_timer(
            "workflow_test",
            duration,
            on_start=[on_start],
            on_end=[on_end]
        )
        assert service.get_timer("workflow_test") == timer
        workflow_events.append("created")
        
        # 3. Start timer
        service.start_timer("workflow_test")
        time.sleep(0.2)
        assert "started" in workflow_events
        
        # 4. Pause timer
        service.pause_or_resume_timer("workflow_test")
        assert timer.status == TimerStatus.PAUSED
        remaining_at_pause = timer.remaining
        workflow_events.append("paused")
        
        # 5. Resume timer
        time.sleep(0.2)
        service.pause_or_resume_timer("workflow_test")
        assert timer.status == TimerStatus.RUNNING
        workflow_events.append("resumed")
        
        # 6. Wait for completion
        time.sleep(2.5)
        assert timer.status == TimerStatus.FINISHED
        assert "finished" in workflow_events
        
        # Verify workflow sequence
        expected_sequence = ["created", "started", "paused", "resumed", "finished"]
        assert workflow_events == expected_sequence

    def test_multiple_timers_workflow(self):
        """Test workflow with multiple timers."""
        service = TimerService()
        
        # Create multiple timers with different durations
        timers_config = [
            ("short", "1s"),
            ("medium", "2s"),
            ("long", "3s"),
        ]
        
        for name, duration_str in timers_config:
            duration = parse_time(duration_str)
            service.create_timer(name, duration)
        
        # Verify all timers are created
        all_timers = service.list_timers()
        assert len(all_timers) == 3
        
        # Start all timers
        for name, _ in timers_config:
            service.start_timer(name)
        
        # Check all are running
        for name, _ in timers_config:
            assert service.get_timer(name).status == TimerStatus.RUNNING
        
        # Wait for short timer to finish
        time.sleep(1.5)
        assert service.get_timer("short").status == TimerStatus.FINISHED
        assert service.get_timer("medium").status == TimerStatus.RUNNING
        assert service.get_timer("long").status == TimerStatus.RUNNING
        
        # Stop medium timer
        service.stop_timer("medium")
        assert service.get_timer("medium").status == TimerStatus.STOPPED
        
        # Wait for long timer
        time.sleep(2)
        assert service.get_timer("long").status == TimerStatus.FINISHED
        
        # Clean up finished timers
        service.remove_timer("short")
        service.remove_timer("long")
        
        # Verify they're removed
        assert service.get_timer("short") is None
        assert service.get_timer("long") is None
        assert service.get_timer("medium") is not None

    def test_timer_with_add_time(self):
        """Test adding time to running timer."""
        service = TimerService()
        
        # Create and start timer
        timer = service.create_timer("extendable", timedelta(seconds=2))
        service.start_timer("extendable")
        
        # Wait a bit
        time.sleep(0.5)
        remaining_before = timer.remaining
        
        # Add extra time
        service.add_time("extendable", timedelta(seconds=1))
        remaining_after = timer.remaining
        
        # Verify time was added
        assert remaining_after > remaining_before
        assert remaining_after - remaining_before >= timedelta(seconds=0.9)


@pytest.mark.integration  
@pytest.mark.slow
class TestStressTest:
    """Stress tests with many timers."""

    def test_many_timers_sequential(self):
        """Test creating and managing many timers sequentially."""
        service = TimerService()
        num_timers = 50
        
        # Create many timers
        for i in range(num_timers):
            service.create_timer(f"timer_{i}", timedelta(seconds=1))
        
        # Verify all created
        all_timers = service.list_timers()
        assert len(all_timers) == num_timers
        
        # Start all timers
        for i in range(num_timers):
            service.start_timer(f"timer_{i}")
        
        # Verify all running
        for i in range(num_timers):
            assert service.get_timer(f"timer_{i}").status == TimerStatus.RUNNING
        
        # Wait for completion
        time.sleep(1.5)
        
        # Verify all finished
        for i in range(num_timers):
            assert service.get_timer(f"timer_{i}").status == TimerStatus.FINISHED

    def test_timer_precision_under_load(self):
        """Test timer precision with multiple concurrent timers."""
        service = TimerService()
        expected_duration = timedelta(seconds=2)
        tolerance = timedelta(milliseconds=600)  # 600ms tolerance for CI/CD
        
        # Create multiple timers with same duration
        for i in range(10):
            service.create_timer(f"precise_{i}", expected_duration)
        
        # Start all and measure
        start_time = time.time()
        for i in range(10):
            service.start_timer(f"precise_{i}")
        
        # Wait for completion
        time.sleep(2.5)
        elapsed = time.time() - start_time
        
        # Verify all finished within tolerance
        for i in range(10):
            timer = service.get_timer(f"precise_{i}")
            assert timer.status == TimerStatus.FINISHED
            # Elapsed time should be close to expected duration
            assert abs(elapsed - expected_duration.total_seconds()) <= tolerance.total_seconds()
