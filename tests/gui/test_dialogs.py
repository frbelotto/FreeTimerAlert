"""Tests for GUI dialog windows."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from src.interfaces.gui.dialogs import AddTimeDialog, CreateTimerDialog


class TestCreateTimerDialog:
    """Tests for CreateTimerDialog functionality."""

    def test_dialog_initialization(self, tk_root):
        """Dialog initializes with correct attributes and widgets."""
        dialog = CreateTimerDialog(tk_root)

        assert dialog.result is None
        assert dialog.dialog_window is not None
        assert isinstance(dialog.dialog_window, tk.Toplevel)
        assert dialog.name_entry is not None
        assert dialog.duration_entry is not None

        dialog.dialog_window.destroy()

    def test_dialog_has_correct_title(self, tk_root):
        """Dialog window displays correct title."""
        dialog = CreateTimerDialog(tk_root)

        assert dialog.dialog_window.title() == "Create Timer"

        dialog.dialog_window.destroy()

    def test_dialog_entry_widgets_exist(self, tk_root):
        """Dialog contains name and duration entry widgets."""
        dialog = CreateTimerDialog(tk_root)

        assert hasattr(dialog, "name_entry")
        assert hasattr(dialog, "duration_entry")
        assert isinstance(dialog.name_entry, tk.Entry)
        assert isinstance(dialog.duration_entry, tk.Entry)

        dialog.dialog_window.destroy()

    @patch("src.interfaces.gui.dialogs.messagebox.showwarning")
    def test_create_with_empty_name_shows_warning(self, mock_warning, tk_root):
        """Creating timer with empty name shows warning."""
        dialog = CreateTimerDialog(tk_root)
        dialog.duration_entry.insert(0, "10m")

        dialog._on_create()

        mock_warning.assert_called_once()
        assert dialog.result is None

        dialog.dialog_window.destroy()

    @patch("src.interfaces.gui.dialogs.messagebox.showwarning")
    def test_create_with_empty_duration_shows_warning(self, mock_warning, tk_root):
        """Creating timer with empty duration shows warning."""
        dialog = CreateTimerDialog(tk_root)
        dialog.name_entry.insert(0, "test")

        dialog._on_create()

        mock_warning.assert_called_once()
        assert dialog.result is None

        dialog.dialog_window.destroy()

    @patch("src.interfaces.gui.dialogs.messagebox.showerror")
    def test_create_with_invalid_duration_shows_error(self, mock_error, tk_root):
        """Creating timer with invalid duration format shows error."""
        dialog = CreateTimerDialog(tk_root)
        dialog.name_entry.insert(0, "test")
        dialog.duration_entry.insert(0, "invalid_format")

        dialog._on_create()

        mock_error.assert_called_once()
        assert dialog.result is None

        dialog.dialog_window.destroy()

    def test_create_with_valid_inputs_sets_result(self, tk_root):
        """Creating timer with valid inputs sets result correctly."""
        dialog = CreateTimerDialog(tk_root)
        dialog.name_entry.insert(0, "test_timer")
        dialog.duration_entry.insert(0, "25m")

        dialog._on_create()

        assert dialog.result == ("test_timer", "25m")

    def test_cancel_sets_result_to_none(self, tk_root):
        """Canceling dialog sets result to None."""
        dialog = CreateTimerDialog(tk_root)
        dialog.name_entry.insert(0, "test")
        dialog.duration_entry.insert(0, "10m")

        dialog._on_cancel()

        assert dialog.result is None

    def test_show_returns_result_after_destroy(self, tk_root):
        """Show method returns result after window is destroyed."""
        dialog = CreateTimerDialog(tk_root)

        # Simular fechamento imediato com resultado antes de chamar show
        dialog.result = ("test", "5m")
        window = dialog.dialog_window
        dialog.dialog_window = None  # Evitar wait_window em janela destruída

        result = dialog.show()

        assert result == ("test", "5m")


class TestAddTimeDialog:
    """Tests for AddTimeDialog functionality."""

    def test_dialog_initialization(self, tk_root):
        """Dialog initializes with correct timer name and attributes."""
        dialog = AddTimeDialog(tk_root, "test_timer")

        assert dialog.timer_name == "test_timer"
        assert dialog.result is None

    def test_dialog_stores_timer_name(self, tk_root):
        """Dialog stores timer name correctly."""
        timer_name = "my_timer"
        dialog = AddTimeDialog(tk_root, timer_name)

        assert dialog.timer_name == timer_name
