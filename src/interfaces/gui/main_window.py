# -*- coding: utf-8 -*-
"""
Main window implementation for FreeTimer GUI using Tkinter.

This module provides the main application window and orchestrates
the GUI components while reusing core business logic.
"""

import logging
import tkinter as tk
import webbrowser
from datetime import timedelta
from pathlib import Path
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from src.interfaces.gui.dialogs import CreateTimerDialog
from src.interfaces.gui.timer_widget import TimerWidget
from src.services.parse_utils import parse_time
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
        self.timer_widgets: dict[str, TimerWidget] = {}  # Track timer widgets by name
        self.notifications_enabled: bool = True  # Controlar notificações sonoras

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
        self.notifications_button = ttk.Button(self.toolbar, text="Sound: ON", command=self._toggle_notifications)

        # Timer list area with scrollable canvas
        self.timer_frame = ttk.LabelFrame(self.main_frame, text="Active Timers", padding="10")

        # Create canvas with scrollbar for timers
        self.timer_canvas = tk.Canvas(self.timer_frame, bg="white", highlightthickness=0)
        self.timer_scrollbar = ttk.Scrollbar(self.timer_frame, orient="vertical", command=self.timer_canvas.yview)
        self.timer_canvas.configure(yscrollcommand=self.timer_scrollbar.set)

        # Frame inside canvas to hold timer widgets
        self.timers_container = ttk.Frame(self.timer_canvas)
        self.timer_canvas.create_window((0, 0), window=self.timers_container, anchor="nw")
        self.timers_container.bind("<Configure>", lambda e: self.timer_canvas.configure(scrollregion=self.timer_canvas.bbox("all")))

        # Placeholder message
        self.empty_label = ttk.Label(self.timer_frame, text="No timers yet. Click 'Create Timer' to get started!", font=("TkDefaultFont", 12), foreground="gray")

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)

    def _setup_layout(self) -> None:
        """Arrange widgets using grid layout."""
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        self.toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.create_button.pack(side=tk.LEFT, padx=(0, 10))
        self.notifications_button.pack(side=tk.LEFT)
        self.timer_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        # Setup timer canvas layout
        self.timer_canvas.grid(row=0, column=0, sticky="nsew")
        self.timer_scrollbar.grid(row=0, column=1, sticky="ns")
        self.empty_label.grid(row=0, column=0, columnspan=2, pady=50)

        self.timer_frame.grid_rowconfigure(0, weight=1)
        self.timer_frame.grid_columnconfigure(0, weight=1)

        self.status_bar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def _create_timer(self) -> None:
        """Handle create timer button click.

        Opens a dialog to create a new timer with user input.
        """
        dialog = CreateTimerDialog(self.root)
        result = dialog.show()

        if result is None:
            logger.debug("Create timer cancelled")
            return

        timer_name, duration_str = result

        # Check if timer name already exists
        if self.timer_service.get_timer(timer_name):
            logger.warning(f"Attempted to create duplicate timer: {timer_name}")
            mb.showerror("Error", f"Timer '{timer_name}' already exists!")
            return

        try:
            # Parse duration string to timedelta
            duration = parse_time(duration_str)

            # Create timer in service
            self.timer_service.create_timer(timer_name, duration)

            # Create and display timer widget
            self._add_timer_widget(timer_name)

            # Update status bar
            self.status_bar.config(text=f"Timer '{timer_name}' created successfully")
            logger.info(f"Timer '{timer_name}' created with duration {duration}")

        except ValueError as e:
            logger.error(f"Failed to create timer '{timer_name}': {e}")
            mb.showerror("Error", f"Failed to create timer: {e}")

    def _add_timer_widget(self, timer_name: str) -> None:
        """Add a timer widget to the display.

        Args:
            timer_name: Name of the timer to display
        """
        # Hide empty label if there are timers
        if not self.timer_widgets:
            self.empty_label.grid_remove()
            self.timer_canvas.grid()
            self.timer_scrollbar.grid()

        # Create and add timer widget with delete callback and notifications setting
        timer_widget = TimerWidget(
            self.timers_container, timer_name, self.timer_service, on_delete_callback=self._on_timer_deleted, notifications_enabled=self.notifications_enabled
        )
        timer_widget.pack(fill=tk.X, padx=(0, 5), pady=5)

        # Store reference
        self.timer_widgets[timer_name] = timer_widget

        logger.debug(f"Timer widget added for '{timer_name}'")

    def _on_timer_deleted(self, timer_name: str) -> None:
        """Handle timer deletion to update empty state.

        Args:
            timer_name: Name of the deleted timer
        """
        # Remove timer widget reference
        if timer_name in self.timer_widgets:
            del self.timer_widgets[timer_name]
            logger.debug(f"Timer widget reference removed for '{timer_name}'")

        # Show empty label if no timers remain
        if not self.timer_widgets:
            self.timer_canvas.grid_remove()
            self.timer_scrollbar.grid_remove()
            self.empty_label.grid()
            self.status_bar.config(text=f"Timer '{timer_name}' deleted")
            logger.debug("No timers remaining, empty label displayed")

    def _toggle_notifications(self) -> None:
        """Toggle sound notifications on/off and update all existing timers."""
        self.notifications_enabled = not self.notifications_enabled

        # Atualizar estado de todos os widgets de timer existentes
        for timer_widget in self.timer_widgets.values():
            timer_widget.notifications_enabled = self.notifications_enabled

        # Atualizar botão
        button_text = "Sound: ON" if self.notifications_enabled else "Sound: OFF"
        self.notifications_button.config(text=button_text)

        status_text = "Sound notifications enabled" if self.notifications_enabled else "Sound notifications disabled"
        self.status_bar.config(text=status_text)
        logger.info(f"Sound notifications toggled: {self.notifications_enabled}")

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

        # GitHub repository link
        def open_github() -> None:
            """Open GitHub repository in default browser."""
            webbrowser.open("https://github.com/frbelotto/FreeTimerAlert")

        ttk.Button(frame, text="View on GitHub", command=open_github).pack()

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
