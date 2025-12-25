# -*- coding: utf-8 -*-
"""
Main window implementation for FreeTimer GUI using Tkinter.

This module provides the main application window and orchestrates
the GUI components while reusing core business logic.
"""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from src.services.timer_service import TimerService

logger = logging.getLogger(__name__)


def _bold_font(size: int) -> tuple[str, int, str]:
    """Return a simple bold default font tuple.
    Simplifica compatibilidade entre Windows/Linux/macOS evitando emojis."""
    return ("TkDefaultFont", size, "bold")


class MainWindow:
    """
    Main application window for FreeTimer GUI.

    Manages the overall application layout and coordinates
    interaction between GUI components and the TimerService.
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize main window.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.timer_service = TimerService()

        self._setup_window()
        self._create_widgets()
        self._setup_layout()

        logger.info("Main window initialized")

    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.root.title("FreeTimer")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View README", command=self._show_readme)
        help_menu.add_command(label="About", command=self._show_about)

        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Title
        self.title_label = ttk.Label(self.main_frame, text="FreeTimer", font=_bold_font(24))

        # Toolbar
        self.toolbar = ttk.Frame(self.main_frame)
        self.create_button = ttk.Button(self.toolbar, text="Create Timer", command=self._create_timer)

        # Timer list area (placeholder)
        self.timer_frame = ttk.LabelFrame(self.main_frame, text="Active Timers", padding="10")

        # Placeholder message
        self.empty_label = ttk.Label(self.timer_frame, text="No timers yet. Click 'Create Timer' to get started!", font=("TkDefaultFont", 12), foreground="gray")

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)

    def _setup_layout(self) -> None:
        """Arrange widgets using grid layout."""
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        self.toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.create_button.pack(side=tk.LEFT)
        self.timer_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.empty_label.pack(pady=50)
        self.status_bar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def _create_timer(self) -> None:
        """Handle create timer button click."""
        # TODO: Implement dialog for timer creation
        self.status_bar.config(text="Create timer dialog - To be implemented")
        logger.info("Create timer button clicked")

    def _show_about(self) -> None:
        """Show about dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About FreeTimer")
        about_window.geometry("400x200")
        about_window.resizable(False, False)

        # Center about window
        about_window.transient(self.root)
        about_window.grab_set()

        frame = ttk.Frame(about_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="FreeTimer", font=_bold_font(16)).pack(pady=(0, 10))

        ttk.Label(frame, text="Simple timer application with clean architecture", wraplength=350).pack(pady=(0, 10))

        ttk.Label(frame, text="Version: 0.2.0", foreground="gray").pack(pady=(0, 5))

        ttk.Label(frame, text="© 2025 - CC BY-NC-SA 4.0", foreground="gray").pack(pady=(0, 20))

        ttk.Button(frame, text="Close", command=about_window.destroy).pack()

    def _show_readme(self) -> None:
        """Display project README.md in a scrollable window.

        Opens a modal window showing the README content for quick reference.
        Shows plain text content for maximum compatibility.
        """
        try:
            root_dir: Path = Path(__file__).resolve().parents[3]
            readme_path: Path = root_dir / "README.md"

            if not readme_path.exists():
                mb.showerror("README not found", f"Could not find README.md at:\n{readme_path}")
                return

            content: str = readme_path.read_text(encoding="utf-8", errors="replace")

            win = tk.Toplevel(self.root)
            win.title("README.md")
            win.geometry("800x600")
            win.resizable(True, True)
            win.transient(self.root)
            win.grab_set()

            frame = ttk.Frame(win, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)

            text = ScrolledText(frame, wrap="word", font=("TkDefaultFont", 11))
            text.pack(fill=tk.BOTH, expand=True)
            text.insert("1.0", content)
            text.configure(state=tk.DISABLED)

            ttk.Button(frame, text="Close", command=win.destroy).pack(pady=(8, 0))

            self.status_bar.config(text=f"README opened: {readme_path}")
            logger.info(f"README displayed from {readme_path}")

        except Exception as e:
            logger.exception(f"Failed to display README: {e}")
            mb.showerror("Error", f"Failed to display README: {e}")

    def run(self) -> None:
        """Start the GUI main loop."""
        logger.info("Starting GUI main loop")
        self.root.mainloop()


def run_gui() -> None:
    """
    Entry point for GUI application.

    Creates and runs the main window.
    """
    root = tk.Tk()
    app = MainWindow(root)
    app.run()
