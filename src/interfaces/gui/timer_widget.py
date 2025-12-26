"""
Timer widget implementation for displaying individual timers in the GUI.

This module provides the visual representation of a single timer
with controls for start, pause, reset, etc.
"""

import logging
import tkinter as tk
from datetime import timedelta
from tkinter import messagebox, ttk
from typing import Callable, Optional

from src.core.timer import TimerStatus
from src.interfaces.terminal.notifications import play_end_sound, play_start_sound, stop_current_sound
from src.services.system_notifications import show_timer_finished_notification
from src.services.timer_service import TimerService

logger = logging.getLogger(__name__)


class TimerWidget(ttk.Frame):
    """
    Widget representing a single timer in the GUI.

    Displays timer information and provides control buttons.
    """

    def __init__(
        self,
        parent: tk.Widget,
        timer_name: str,
        timer_service: TimerService,
        on_delete_callback: Optional[Callable[[str], None]] = None,
        notifications_enabled: bool = True,
    ) -> None:
        """
        Initialize timer widget.

        Args:
            parent: Parent widget
            timer_name: Name of the timer to display
            timer_service: Timer service instance
            on_delete_callback: Callback function to call when timer is deleted
            notifications_enabled: Whether sound notifications are enabled
        """
        super().__init__(parent, relief=tk.RAISED, borderwidth=1, padding="10")
        self.timer_name = timer_name
        self.timer_service = timer_service
        self.timer = timer_service.get_timer(timer_name)
        self.update_job: str | None = None
        self.on_delete_callback = on_delete_callback
        self.previous_status: TimerStatus | None = None  # Rastrear mudanças de estado
        self.notifications_enabled = notifications_enabled  # Controlar ativação de som

        self._create_widgets()
        self._setup_layout()
        self._start_update_loop()

        logger.debug(f"Timer widget created for '{timer_name}'")

    def _create_widgets(self) -> None:
        """Create widget components."""
        # Info frame (name and time display)
        info_frame = ttk.Frame(self)

        # Timer name
        name_label = ttk.Label(info_frame, text=self.timer_name, font=("TkDefaultFont", 12, "bold"))
        name_label.pack(side=tk.LEFT, padx=(0, 20))

        # Time display
        self.time_label = ttk.Label(info_frame, text="00:00:00", font=("TkDefaultFont", 14, "bold"), foreground="blue")
        self.time_label.pack(side=tk.LEFT)

        # Status label
        self.status_label = ttk.Label(info_frame, text="Idle", font=("TkDefaultFont", 10), foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        # Control buttons frame
        button_frame = ttk.Frame(self)

        self.start_button = ttk.Button(button_frame, text="Start", command=self._on_start)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))

        self.pause_button = ttk.Button(button_frame, text="Pause", command=self._on_pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self._on_reset)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self._on_delete)
        self.delete_button.pack(side=tk.LEFT)

        # Store frames for layout
        self.info_frame = info_frame
        self.button_frame = button_frame

    def _setup_layout(self) -> None:
        """Arrange widgets using pack layout."""
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        self.button_frame.pack(fill=tk.X)

    def _update_display(self) -> None:
        """Update timer display and reschedule update."""
        if not self.timer:
            return

        # Update time display
        remaining = self.timer.remaining
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_label.config(text=time_str)

        # Update status
        status_text = self.timer.status.value
        status_color_map = {
            TimerStatus.IDLE: "gray",
            TimerStatus.RUNNING: "green",
            TimerStatus.PAUSED: "orange",
            TimerStatus.FINISHED: "red",
            TimerStatus.STOPPED: "red",
        }
        color = status_color_map.get(self.timer.status, "gray")
        self.status_label.config(text=status_text, foreground=color)

        # Detectar mudanças de estado e tocar sons  # Notifica mudanças de estado com áudio
        self._handle_status_change()

        # Update button states
        self._update_button_states()

        # Reschedule update
        if self.timer.status == TimerStatus.RUNNING:
            self.update_job = self.after(100, self._update_display)
        else:
            self.update_job = self.after(500, self._update_display)

    def _update_button_states(self) -> None:
        """Update button enabled/disabled states based on timer status."""
        if not self.timer:
            return

        if self.timer.status == TimerStatus.IDLE:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        elif self.timer.status == TimerStatus.RUNNING:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
        elif self.timer.status == TimerStatus.PAUSED:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.DISABLED)
        elif self.timer.status in (TimerStatus.FINISHED, TimerStatus.STOPPED):
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)

    def _handle_status_change(self) -> None:
        """Detect status changes and play notification sounds."""
        current_status = self.timer.status

        if not self.notifications_enabled:
            self.previous_status = current_status
            return

        # Parar som quando timer é pausado
        if self.previous_status == TimerStatus.RUNNING and current_status == TimerStatus.PAUSED:
            try:
                stop_current_sound()
            except Exception as e:
                logger.warning(f"Failed to stop sound: {e}")

        # Tocar som quando timer inicia ou retoma
        if self.previous_status != TimerStatus.RUNNING and current_status == TimerStatus.RUNNING:
            try:
                play_start_sound()
            except Exception as e:
                logger.warning(f"Failed to play start sound: {e}")

        # Tocar som e mostrar notificação visual quando timer termina
        if current_status in (TimerStatus.FINISHED, TimerStatus.STOPPED):
            if self.previous_status not in (TimerStatus.FINISHED, TimerStatus.STOPPED):
                try:
                    play_end_sound()
                except Exception as e:
                    logger.warning(f"Failed to play end sound: {e}")

                try:
                    show_timer_finished_notification(self.timer_name)
                except Exception as e:
                    logger.warning(f"Failed to show system notification: {e}")

        self.previous_status = current_status

    def _start_update_loop(self) -> None:
        """Start the update loop."""
        self._update_display()

    def _on_start(self) -> None:
        """Handle start button click."""
        try:
            self.timer_service.start_timer(self.timer_name)
            logger.debug(f"Started timer '{self.timer_name}'")
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to start timer: {e}")

    def _on_pause(self) -> None:
        """Handle pause button click."""
        try:
            self.timer_service.pause_or_resume_timer(self.timer_name)
            logger.debug(f"Paused/Resumed timer '{self.timer_name}'")
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to pause timer: {e}")

    def _on_reset(self) -> None:
        """Handle reset button click."""
        try:
            self.timer_service.reset_timer(self.timer_name)
            logger.debug(f"Reset timer '{self.timer_name}'")
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to reset timer: {e}")

    def _on_delete(self) -> None:
        """Handle delete button click."""
        try:
            self.timer_service.remove_timer(self.timer_name)
            logger.debug(f"Deleted timer '{self.timer_name}'")

            # Cancel update job
            if self.update_job:
                self.after_cancel(self.update_job)

            # Call deletion callback if provided
            if self.on_delete_callback:
                self.on_delete_callback(self.timer_name)

            # Remove widget from parent
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to delete timer: {e}")

    def destroy(self) -> None:
        """Override destroy to cancel update job."""
        if self.update_job:
            self.after_cancel(self.update_job)
        super().destroy()
