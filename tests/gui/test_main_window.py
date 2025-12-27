"""Tests for MainWindow GUI component."""

import tkinter as tk
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.interfaces.gui.main_window import MainWindow


class TestMainWindowInitialization:
    """Tests for MainWindow initialization."""

    def test_window_initialization(self, tk_root):
        """Window initializes with correct attributes."""
        window = MainWindow(tk_root)

        assert window.root is tk_root
        assert window.timer_service is not None
        assert window.timer_widgets == {}
        assert window.notifications_enabled is True

    def test_window_has_title(self, tk_root):
        """Window has correct title."""
        window = MainWindow(tk_root)

        assert tk_root.title() == "FreeTimer"

    def test_window_has_minimum_size(self, tk_root):
        """Window has minimum size set."""
        window = MainWindow(tk_root)

        assert tk_root.minsize() == (600, 400)

    def test_window_creates_main_frame(self, tk_root):
        """Window creates main container frame."""
        window = MainWindow(tk_root)

        assert hasattr(window, "main_frame")
        assert isinstance(window.main_frame, (tk.Frame, tk.ttk.Frame))

    def test_window_creates_toolbar(self, tk_root):
        """Window creates toolbar with buttons."""
        window = MainWindow(tk_root)

        assert hasattr(window, "toolbar")
        assert hasattr(window, "create_button")
        assert hasattr(window, "notifications_button")

    def test_window_creates_timer_frame(self, tk_root):
        """Window creates frame for timer widgets."""
        window = MainWindow(tk_root)

        assert hasattr(window, "timer_frame")
        assert hasattr(window, "timer_canvas")
        assert hasattr(window, "timers_container")

    def test_window_creates_status_bar(self, tk_root):
        """Window creates status bar."""
        window = MainWindow(tk_root)

        assert hasattr(window, "status_bar")
        assert window.status_bar.cget("text") == "Ready"


class TestMainWindowTimerCreation:
    """Tests for timer creation functionality."""

    @patch("src.interfaces.gui.main_window.CreateTimerDialog")
    def test_create_timer_opens_dialog(self, mock_dialog_class, tk_root):
        """Create timer button opens dialog."""
        window = MainWindow(tk_root)
        mock_dialog = Mock()
        mock_dialog.show.return_value = None
        mock_dialog_class.return_value = mock_dialog

        window._create_timer()

        mock_dialog_class.assert_called_once_with(tk_root)
        mock_dialog.show.assert_called_once()

    @patch("src.interfaces.gui.main_window.CreateTimerDialog")
    def test_create_timer_with_valid_input(self, mock_dialog_class, tk_root):
        """Creating timer with valid input adds timer to service."""
        window = MainWindow(tk_root)
        mock_dialog = Mock()
        mock_dialog.show.return_value = ("test_timer", "10m")
        mock_dialog_class.return_value = mock_dialog

        window._create_timer()

        # Verify timer was created in service
        timer = window.timer_service.get_timer("test_timer")
        assert timer is not None
        assert timer.duration == timedelta(minutes=10)

    @patch("src.interfaces.gui.main_window.CreateTimerDialog")
    def test_create_timer_canceled(self, mock_dialog_class, tk_root):
        """Canceling timer creation doesn't create timer."""
        window = MainWindow(tk_root)
        mock_dialog = Mock()
        mock_dialog.show.return_value = None
        mock_dialog_class.return_value = mock_dialog

        window._create_timer()

        # Verify no timer was created
        assert len(window.timer_service.list_timers()) == 0

    @patch("src.interfaces.gui.main_window.mb.showerror")
    @patch("src.interfaces.gui.main_window.CreateTimerDialog")
    def test_create_duplicate_timer_shows_error(self, mock_dialog_class, mock_error, tk_root):
        """Creating timer with duplicate name shows error."""
        window = MainWindow(tk_root)

        # Create first timer
        window.timer_service.create_timer("test", timedelta(minutes=5))

        # Try to create duplicate
        mock_dialog = Mock()
        mock_dialog.show.return_value = ("test", "10m")
        mock_dialog_class.return_value = mock_dialog

        window._create_timer()

        mock_error.assert_called_once()


class TestMainWindowTimerWidget:
    """Tests for timer widget management."""

    def test_add_timer_widget(self, tk_root):
        """Adding timer widget creates and stores widget reference."""
        window = MainWindow(tk_root)
        window.timer_service.create_timer("test", timedelta(minutes=5))

        window._add_timer_widget("test")

        assert "test" in window.timer_widgets
        assert window.timer_widgets["test"] is not None

    def test_add_timer_widget_hides_empty_label(self, tk_root):
        """Adding first timer widget hides empty label."""
        window = MainWindow(tk_root)
        window.timer_service.create_timer("test", timedelta(minutes=5))

        # Atualizar idletasks para que grid tenha efeito
        tk_root.update_idletasks()

        window._add_timer_widget("test")
        tk_root.update_idletasks()

        # Empty label should be removed from grid
        assert window.empty_label.grid_info() == {}
        # Canvas and scrollbar should be in grid
        assert window.timer_canvas.grid_info() != {}
        assert window.timer_scrollbar.grid_info() != {}

    def test_remove_timer_widget_reference(self, tk_root):
        """Removing timer widget deletes reference."""
        window = MainWindow(tk_root)
        window.timer_service.create_timer("test", timedelta(minutes=5))
        window._add_timer_widget("test")

        window._on_timer_deleted("test")

        assert "test" not in window.timer_widgets

    def test_remove_last_timer_shows_empty_label(self, tk_root):
        """Removing last timer shows empty label."""
        window = MainWindow(tk_root)
        window.timer_service.create_timer("test", timedelta(minutes=5))
        window._add_timer_widget("test")
        tk_root.update_idletasks()

        window._on_timer_deleted("test")
        tk_root.update_idletasks()

        # Empty label should be back in grid
        assert window.empty_label.grid_info() != {}
        # Canvas and scrollbar should be removed from grid
        assert window.timer_canvas.grid_info() == {}
        assert window.timer_scrollbar.grid_info() == {}

    def test_multiple_timer_widgets(self, tk_root):
        """Can create and manage multiple timer widgets."""
        window = MainWindow(tk_root)

        for i in range(3):
            timer_name = f"timer{i}"
            window.timer_service.create_timer(timer_name, timedelta(minutes=5))
            window._add_timer_widget(timer_name)

        assert len(window.timer_widgets) == 3
        assert "timer0" in window.timer_widgets
        assert "timer1" in window.timer_widgets
        assert "timer2" in window.timer_widgets


class TestMainWindowNotifications:
    """Tests for notification toggle functionality."""

    def test_toggle_notifications_initial_state(self, tk_root):
        """Notifications are enabled by default."""
        window = MainWindow(tk_root)

        assert window.notifications_enabled is True
        assert window.notifications_button.cget("text") == "Sound: ON"

    def test_toggle_notifications_disables(self, tk_root):
        """Toggling notifications disables them."""
        window = MainWindow(tk_root)

        window._toggle_notifications()

        assert window.notifications_enabled is False
        assert window.notifications_button.cget("text") == "Sound: OFF"

    def test_toggle_notifications_enables(self, tk_root):
        """Toggling notifications again enables them."""
        window = MainWindow(tk_root)

        window._toggle_notifications()
        window._toggle_notifications()

        assert window.notifications_enabled is True
        assert window.notifications_button.cget("text") == "Sound: ON"

    def test_toggle_updates_existing_widgets(self, tk_root):
        """Toggling notifications updates existing timer widgets."""
        window = MainWindow(tk_root)
        window.timer_service.create_timer("test", timedelta(minutes=5))
        window._add_timer_widget("test")

        widget = window.timer_widgets["test"]
        assert widget.notifications_enabled is True

        window._toggle_notifications()

        assert widget.notifications_enabled is False


class TestMainWindowDialogs:
    """Tests for about and readme dialogs."""

    def test_show_about_opens_window(self, tk_root):
        """Show about creates about window."""
        window = MainWindow(tk_root)

        # Track number of children before and after
        children_before = len(tk_root.winfo_children())

        # Patch Toplevel to track calls
        from tkinter import Toplevel as ToplevelClass

        with patch("src.interfaces.gui.main_window.tk.Toplevel", wraps=ToplevelClass) as mock_toplevel:
            window._show_about()

            # Verify Toplevel was called to create about window
            mock_toplevel.assert_called_once_with(tk_root)

            # Clean up created windows
            for widget in list(tk_root.winfo_children()):
                if isinstance(widget, ToplevelClass):
                    widget.destroy()

    @patch("src.interfaces.gui.main_window.Path.exists")
    @patch("src.interfaces.gui.main_window.Path.read_text")
    def test_show_readme_with_existing_file(self, mock_read, mock_exists, tk_root):
        """Show readme displays content when file exists."""
        window = MainWindow(tk_root)
        mock_exists.return_value = True
        mock_read.return_value = "# README Content"

        # Usar wraps ao invés de mock puro para permitir criação de widgets internos
        from tkinter import Toplevel as ToplevelClass

        with patch("src.interfaces.gui.main_window.tk.Toplevel", wraps=ToplevelClass) as mock_toplevel:
            window._show_readme()

            # Verificar que Toplevel foi chamado
            mock_toplevel.assert_called_once()

            # Limpar janelas criadas
            for widget in list(tk_root.winfo_children()):
                if isinstance(widget, ToplevelClass):
                    widget.destroy()

    @patch("src.interfaces.gui.main_window.mb.showerror")
    @patch("src.interfaces.gui.main_window.Path.exists")
    def test_show_readme_with_missing_file(self, mock_exists, mock_error, tk_root):
        """Show readme displays error when file missing."""
        window = MainWindow(tk_root)
        mock_exists.return_value = False

        window._show_readme()

        mock_error.assert_called_once()


class TestMainWindowRun:
    """Tests for main window run method."""

    def test_run_starts_mainloop(self, tk_root):
        """Run method starts Tkinter mainloop."""
        window = MainWindow(tk_root)

        with patch.object(tk_root, "mainloop") as mock_mainloop:
            window.run()
            mock_mainloop.assert_called_once()
