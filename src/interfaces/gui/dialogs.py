"""
Dialog windows for FreeTimer GUI.

This module provides dialog windows for user interactions such as
creating new timers, adding time, and confirmations.
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from src.services.parse_utils import parse_time

logger = logging.getLogger(__name__)


class CreateTimerDialog:
    """
    Dialog for creating a new timer.

    Allows user to input timer name and duration.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """
        Initialize create timer dialog.

        Args:
            parent: Parent window
        """
        self.result: Optional[tuple[str, str]] = None
        self.dialog_window: Optional[tk.Toplevel] = None
        self._setup_dialog(parent)
        logger.debug("Create timer dialog initialized")

    def _setup_dialog(self, parent: tk.Widget) -> None:
        """Create and setup the dialog window.

        Args:
            parent: Parent widget for the dialog
        """
        self.dialog_window = tk.Toplevel(parent)
        self.dialog_window.title("Create Timer")
        self.dialog_window.geometry("400x250")
        self.dialog_window.resizable(False, False)
        self.dialog_window.transient(parent)
        self.dialog_window.grab_set()

        # Main frame with padding
        main_frame = ttk.Frame(self.dialog_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Create New Timer", font=("TkDefaultFont", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Timer name field
        ttk.Label(main_frame, text="Timer Name:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        self.name_entry.focus()

        # Duration field with help text
        ttk.Label(main_frame, text="Duration:").grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.duration_entry = ttk.Entry(main_frame, width=30)
        self.duration_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0))

        # Help text for duration format
        help_text = ttk.Label(main_frame, text="Format: 1h30m45s, 45s, 2h15m, etc.", font=("TkDefaultFont", 9), foreground="gray")
        help_text.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        create_btn = ttk.Button(button_frame, text="Create", command=self._on_create)
        create_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.pack(side=tk.LEFT)

        # Configure column weights
        main_frame.columnconfigure(1, weight=1)

        # Bind Enter key to create timer
        self.dialog_window.bind("<Return>", lambda e: self._on_create())

    def _on_create(self) -> None:
        """Handle create button click.

        Validates inputs and returns the result.
        """
        name = self.name_entry.get().strip()
        duration_str = self.duration_entry.get().strip()

        # Validate name
        if not name:
            logger.debug("Empty timer name provided")
            messagebox.showwarning("Invalid Input", "Please enter a timer name.")
            self.name_entry.focus()
            return

        # Validate duration
        if not duration_str:
            logger.debug("Empty duration provided")
            messagebox.showwarning("Invalid Input", "Please enter a duration.")
            self.duration_entry.focus()
            return

        # Try to parse duration
        try:
            parse_time(duration_str)
        except ValueError as e:
            logger.debug(f"Invalid duration format: {duration_str}")
            messagebox.showerror("Invalid Duration", str(e))
            self.duration_entry.focus()
            return

        # Store result and close dialog
        self.result = (name, duration_str)
        logger.debug(f"Timer created with name='{name}', duration='{duration_str}'")
        self.dialog_window.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = None
        logger.debug("Timer creation cancelled")
        self.dialog_window.destroy()

    def show(self) -> Optional[tuple[str, str]]:
        """Show the dialog and wait for user input.

        Returns:
            Tuple of (name, duration) or None if cancelled.
        """
        if self.dialog_window:
            self.dialog_window.wait_window()
        return self.result


class AddTimeDialog:
    """
    Dialog for adding time to an existing timer.

    Allows user to specify additional duration to add.
    """

    def __init__(self, parent: tk.Widget, timer_name: str) -> None:
        """
        Initialize add time dialog.

        Args:
            parent: Parent window
            timer_name: Name of timer to add time to
        """
        self.timer_name = timer_name
        self.result: Optional[str] = None

        # TODO: Implement dialog UI
        logger.debug(f"Add time dialog initialized for '{timer_name}'")
