"""Tests for TimerWidget GUI component."""

import tkinter as tk
from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from src.core.timer import TimerStatus
from src.interfaces.gui.timer_widget import TimerWidget
from src.services.timer_service import TimerService


class TestTimerWidgetInitialization:
    """Tests for TimerWidget initialization and setup."""

    def test_widget_initialization(self, tk_root, timer_service):
        """Widget initializes with correct attributes."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)

        assert widget.timer_name == "test"
        assert widget.timer_service is timer_service
        assert widget.timer is not None
        assert widget.on_delete_callback is None
        assert widget.notifications_enabled is True

        widget.destroy()

    def test_widget_with_callback(self, tk_root, timer_service, mock_callback):
        """Widget accepts and stores delete callback."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service, on_delete_callback=mock_callback)

        assert widget.on_delete_callback is mock_callback

        widget.destroy()

    def test_widget_with_notifications_disabled(self, tk_root, timer_service):
        """Widget can be initialized with notifications disabled."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service, notifications_enabled=False)

        assert widget.notifications_enabled is False

        widget.destroy()

    def test_widget_creates_control_buttons(self, tk_root, timer_service):
        """Widget creates all necessary control buttons."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)

        assert hasattr(widget, "start_button")
        assert hasattr(widget, "pause_button")
        assert hasattr(widget, "reset_button")
        assert hasattr(widget, "delete_button")

        widget.destroy()

    def test_widget_creates_display_labels(self, tk_root, timer_service):
        """Widget creates time and status labels."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)

        assert hasattr(widget, "time_label")
        assert hasattr(widget, "status_label")

        widget.destroy()


class TestTimerWidgetDisplay:
    """Tests for TimerWidget display updates."""

    def test_time_label_initial_format(self, tk_root, timer_service):
        """Time label displays correct initial format."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_display()

        time_text = widget.time_label.cget("text")
        assert time_text == "00:05:00"

        widget.destroy()

    def test_time_label_with_hours(self, tk_root, timer_service):
        """Time label correctly displays hours."""
        timer_service.create_timer("test", timedelta(hours=2, minutes=30))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_display()

        time_text = widget.time_label.cget("text")
        assert time_text == "02:30:00"

        widget.destroy()

    def test_status_label_idle(self, tk_root, timer_service):
        """Status label shows idle state correctly."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_display()

        status_text = widget.status_label.cget("text")
        assert status_text == TimerStatus.IDLE.value

        widget.destroy()

    def test_status_label_running(self, tk_root, timer_service):
        """Status label shows running state correctly."""
        timer_service.create_timer("test", timedelta(seconds=2))
        timer_service.start_timer("test")

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_display()

        status_text = widget.status_label.cget("text")
        assert status_text == TimerStatus.RUNNING.value

        timer_service.stop_timer("test")
        widget.destroy()


class TestTimerWidgetButtonStates:
    """Tests for TimerWidget button state management."""

    def test_buttons_idle_state(self, tk_root, timer_service):
        """Buttons in correct state when timer is idle."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_button_states()

        assert str(widget.start_button.cget("state")) == "normal"
        assert str(widget.pause_button.cget("state")) == "disabled"
        assert str(widget.reset_button.cget("state")) == "normal"
        assert str(widget.delete_button.cget("state")) == "normal"

        widget.destroy()

    def test_buttons_running_state(self, tk_root, timer_service):
        """Buttons in correct state when timer is running."""
        timer_service.create_timer("test", timedelta(seconds=2))
        timer_service.start_timer("test")

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_button_states()

        assert str(widget.start_button.cget("state")) == "disabled"
        assert str(widget.pause_button.cget("state")) == "normal"
        assert str(widget.reset_button.cget("state")) == "disabled"
        assert str(widget.delete_button.cget("state")) == "disabled"

        timer_service.stop_timer("test")
        widget.destroy()

    def test_buttons_paused_state(self, tk_root, timer_service):
        """Buttons in correct state when timer is paused."""
        timer_service.create_timer("test", timedelta(seconds=2))
        timer_service.start_timer("test")
        timer_service.pause_or_resume_timer("test")

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._update_button_states()

        assert str(widget.start_button.cget("state")) == "normal"
        assert str(widget.pause_button.cget("state")) == "normal"
        assert str(widget.reset_button.cget("state")) == "normal"
        assert str(widget.delete_button.cget("state")) == "disabled"

        timer_service.stop_timer("test")
        widget.destroy()


class TestTimerWidgetActions:
    """Tests for TimerWidget action handlers."""

    def test_start_button_starts_timer(self, tk_root, timer_service):
        """Start button calls timer service start."""
        timer_service.create_timer("test", timedelta(seconds=2))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._on_start()

        timer = timer_service.get_timer("test")
        assert timer.status == TimerStatus.RUNNING

        timer_service.stop_timer("test")
        widget.destroy()

    def test_pause_button_pauses_timer(self, tk_root, timer_service):
        """Pause button toggles timer pause state."""
        timer_service.create_timer("test", timedelta(seconds=2))
        timer_service.start_timer("test")

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._on_pause()

        timer = timer_service.get_timer("test")
        assert timer.status == TimerStatus.PAUSED

        timer_service.stop_timer("test")
        widget.destroy()

    def test_reset_button_resets_timer(self, tk_root, timer_service):
        """Reset button resets timer to initial state."""
        timer_service.create_timer("test", timedelta(seconds=2))
        timer_service.start_timer("test")

        widget = TimerWidget(tk_root, "test", timer_service)
        timer_service.stop_timer("test")
        widget._on_reset()

        timer = timer_service.get_timer("test")
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining == timer.duration

        widget.destroy()

    def test_delete_button_removes_timer(self, tk_root, timer_service):
        """Delete button removes timer from service."""
        timer_service.create_timer("test", timedelta(seconds=2))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._on_delete()

        assert timer_service.get_timer("test") is None

    def test_delete_calls_callback(self, tk_root, timer_service, mock_callback):
        """Delete button calls callback with timer name."""
        timer_service.create_timer("test", timedelta(seconds=2))

        widget = TimerWidget(tk_root, "test", timer_service, on_delete_callback=mock_callback)
        widget._on_delete()

        mock_callback.assert_called_once_with("test")


class TestTimerWidgetNotifications:
    """Tests for TimerWidget notification handling."""

    @patch("src.interfaces.gui.timer_widget.play_start_sound")
    def test_start_sound_plays_when_enabled(self, mock_play_start, tk_root, timer_service):
        """Start sound plays when notifications enabled."""
        timer_service.create_timer("test", timedelta(seconds=2))

        widget = TimerWidget(tk_root, "test", timer_service, notifications_enabled=True)
        widget.previous_status = TimerStatus.IDLE
        widget.timer.start()
        widget._handle_status_change()

        mock_play_start.assert_called_once()

        timer_service.stop_timer("test")
        widget.destroy()

    @patch("src.interfaces.gui.timer_widget.play_start_sound")
    def test_start_sound_not_plays_when_disabled(self, mock_play_start, tk_root, timer_service):
        """Start sound doesn't play when notifications disabled."""
        timer_service.create_timer("test", timedelta(seconds=2))

        widget = TimerWidget(tk_root, "test", timer_service, notifications_enabled=False)
        widget.previous_status = TimerStatus.IDLE
        widget.timer.start()
        widget._handle_status_change()

        mock_play_start.assert_not_called()

        timer_service.stop_timer("test")
        widget.destroy()

    @patch("src.interfaces.gui.timer_widget.stop_current_sound")
    def test_sound_stops_on_pause(self, mock_stop_sound, tk_root, timer_service):
        """Sound stops when timer is paused."""
        timer_service.create_timer("test", timedelta(seconds=2))
        timer_service.start_timer("test")

        widget = TimerWidget(tk_root, "test", timer_service, notifications_enabled=True)
        widget.previous_status = TimerStatus.RUNNING
        timer_service.pause_or_resume_timer("test")
        widget._handle_status_change()

        mock_stop_sound.assert_called_once()

        timer_service.stop_timer("test")
        widget.destroy()

    @patch("src.interfaces.gui.timer_widget.play_end_sound")
    @patch("src.interfaces.gui.timer_widget.show_timer_finished_notification")
    def test_end_notification_on_finish(self, mock_notification, mock_play_end, tk_root, timer_service):
        """End sound and notification triggered when timer finishes."""
        timer_service.create_timer("test", timedelta(seconds=1))

        widget = TimerWidget(tk_root, "test", timer_service, notifications_enabled=True)
        widget.previous_status = TimerStatus.RUNNING
        widget.timer.status = TimerStatus.FINISHED
        widget._handle_status_change()

        mock_play_end.assert_called_once()
        mock_notification.assert_called_once_with("test")

        widget.destroy()


class TestTimerWidgetCleanup:
    """Tests for TimerWidget cleanup and destruction."""

    def test_destroy_cancels_update_job(self, tk_root, timer_service):
        """Destroying widget cancels scheduled update job."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)
        widget._start_update_loop()

        assert widget.update_job is not None

        widget.destroy()

        # Verificar que não há erro ao tentar destruir novamente
        # (update_job foi cancelado corretamente)

    def test_widget_handles_missing_timer(self, tk_root, timer_service):
        """Widget handles case where timer is removed externally."""
        timer_service.create_timer("test", timedelta(minutes=5))

        widget = TimerWidget(tk_root, "test", timer_service)

        # Remove timer externally
        timer_service.remove_timer("test")
        widget.timer = None

        # Should not crash when updating
        widget._update_display()

        widget.destroy()
