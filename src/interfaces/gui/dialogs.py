"""
Dialog windows for FreeTimer GUI.

This module provides dialog windows for user interactions such as
creating new timers, adding time, and confirmations.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

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
        
        # TODO: Implement dialog UI
        logger.debug("Create timer dialog initialized")


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
