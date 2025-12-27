"""Tests for terminal interface module."""

from datetime import timedelta
from io import StringIO
from unittest.mock import Mock, call, patch

import pytest

from src.core.timer import Timer, TimerStatus
from src.interfaces.terminal.interface import TerminalInterface
from src.services.timer_service import TimerService


class TestTerminalInterfaceInitialization:
    """Tests for TerminalInterface initialization."""

    def test_interface_creates_timer_service(self):
        """TerminalInterface initializes with a TimerService instance."""
        interface = TerminalInterface()

        assert isinstance(interface.service, TimerService)
        assert interface.service is not None


class TestCreateCallbacks:
    """Tests for callback creation functionality."""

    def test_create_callbacks_returns_two_lists(self):
        """_create_callbacks returns tuple of two callback lists."""
        interface = TerminalInterface()

        on_start, on_end = interface._create_callbacks("test_timer")

        assert isinstance(on_start, list)
        assert isinstance(on_end, list)
        assert len(on_start) == 1
        assert len(on_end) == 1

    @patch("src.interfaces.terminal.interface.play_start_sound")
    @patch("src.interfaces.terminal.interface.print")
    def test_on_start_callback_prints_message(self, mock_print, mock_sound):
        """on_start callback prints start message."""
        interface = TerminalInterface()
        on_start, _ = interface._create_callbacks("my_timer")

        mock_timer = Mock()
        on_start[0](mock_timer)

        # Verifica que print foi chamado com mensagem de início
        assert mock_print.called
        call_args = str(mock_print.call_args)
        assert "my_timer" in call_args
        assert "started" in call_args.lower()

    @patch("src.interfaces.terminal.interface.play_end_sound")
    @patch("src.interfaces.terminal.interface.print")
    def test_on_end_callback_prints_message(self, mock_print, mock_sound):
        """on_end callback prints finish message."""
        interface = TerminalInterface()
        _, on_end = interface._create_callbacks("my_timer")

        mock_timer = Mock()
        on_end[0](mock_timer)

        # Verifica que print foi chamado com mensagem de fim
        assert mock_print.called
        call_args = str(mock_print.call_args)
        assert "my_timer" in call_args
        assert "finished" in call_args.lower()

    @patch("src.interfaces.terminal.interface.play_start_sound")
    @patch("src.interfaces.terminal.interface.print")
    def test_on_start_callback_handles_sound_exception(self, mock_print, mock_sound):
        """on_start callback handles sound playback errors gracefully."""
        mock_sound.side_effect = Exception("Sound error")
        interface = TerminalInterface()
        on_start, _ = interface._create_callbacks("test")

        mock_timer = Mock()
        # Should not raise exception
        on_start[0](mock_timer)

    @patch("src.interfaces.terminal.interface.play_end_sound")
    @patch("src.interfaces.terminal.interface.print")
    def test_on_end_callback_handles_sound_exception(self, mock_print, mock_sound):
        """on_end callback handles sound playback errors gracefully."""
        mock_sound.side_effect = Exception("Sound error")
        interface = TerminalInterface()
        _, on_end = interface._create_callbacks("test")

        mock_timer = Mock()
        # Should not raise exception
        on_end[0](mock_timer)


class TestPrintTimer:
    """Tests for timer display functionality."""

    @patch("src.interfaces.terminal.interface.print")
    def test_print_timer_displays_name_and_status(self, mock_print):
        """_print_timer displays timer name and status."""
        interface = TerminalInterface()
        mock_timer = Mock()
        mock_timer.duration = timedelta(minutes=5)
        mock_timer.remaining = timedelta(minutes=3)
        mock_timer.status = Mock()
        mock_timer.status.value = "running"

        interface._print_timer("test_timer", mock_timer)

        assert mock_print.call_count >= 2  # Pelo menos 2 linhas impressas
        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "test_timer" in call_args_str

    @patch("src.interfaces.terminal.interface.print")
    def test_print_timer_formats_duration(self, mock_print):
        """_print_timer formats duration correctly."""
        interface = TerminalInterface()
        mock_timer = Mock()
        mock_timer.duration = timedelta(hours=1, minutes=30)
        mock_timer.remaining = timedelta(minutes=45)
        mock_timer.status = Mock()
        mock_timer.status.value = "idle"

        interface._print_timer("timer1", mock_timer)

        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "1:30:00" in call_args_str or "01:30:00" in call_args_str


class TestShowMenu:
    """Tests for menu display functionality."""

    @patch("src.interfaces.terminal.interface.print")
    def test_show_menu_displays_all_commands(self, mock_print):
        """show_menu displays all available commands."""
        interface = TerminalInterface()

        interface.show_menu()

        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "create" in call_args_str.lower()
        assert "list" in call_args_str.lower()
        assert "start" in call_args_str.lower()
        assert "pause" in call_args_str.lower()
        assert "reset" in call_args_str.lower()
        assert "add" in call_args_str.lower()
        assert "remove" in call_args_str.lower()
        assert "help" in call_args_str.lower()
        assert "exit" in call_args_str.lower()


class TestCommandCreate:
    """Tests for create timer command."""

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", side_effect=["my_timer", "5m"])
    def test_cmd_criar_creates_timer_successfully(self, mock_input, mock_print):
        """_cmd_criar creates timer with valid inputs."""
        interface = TerminalInterface()

        interface._cmd_criar()

        timer = interface.service.get_timer("my_timer")
        assert timer is not None
        assert timer.duration == timedelta(minutes=5)

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", side_effect=["bad_timer", "invalid_format"])
    def test_cmd_criar_handles_invalid_duration(self, mock_input, mock_print):
        """_cmd_criar handles invalid duration format gracefully."""
        interface = TerminalInterface()

        interface._cmd_criar()

        # Timer should not be created
        timer = interface.service.get_timer("bad_timer")
        assert timer is None

        # Error message should be printed
        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "error" in call_args_str.lower() or "❌" in call_args_str


class TestCommandList:
    """Tests for list timers command."""

    @patch("src.interfaces.terminal.interface.print")
    def test_cmd_listar_shows_no_timers_message(self, mock_print):
        """_cmd_listar shows message when no timers exist."""
        interface = TerminalInterface()

        interface._cmd_listar()

        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "no timers" in call_args_str.lower() or "📭" in call_args_str

    @patch("src.interfaces.terminal.interface.print")
    def test_cmd_listar_displays_existing_timers(self, mock_print):
        """_cmd_listar displays all existing timers."""
        interface = TerminalInterface()
        interface.service.create_timer("timer1", timedelta(minutes=5))
        interface.service.create_timer("timer2", timedelta(minutes=10))

        interface._cmd_listar()

        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "timer1" in call_args_str
        assert "timer2" in call_args_str


class TestCommandStart:
    """Tests for start timer command."""

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", return_value="test_timer")
    def test_cmd_iniciar_starts_existing_timer(self, mock_input, mock_print):
        """_cmd_iniciar starts an existing timer."""
        interface = TerminalInterface()
        interface.service.create_timer("test_timer", timedelta(seconds=30))

        interface._cmd_iniciar()

        timer = interface.service.get_timer("test_timer")
        assert timer.status == TimerStatus.RUNNING

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", return_value="nonexistent")
    def test_cmd_iniciar_handles_missing_timer(self, mock_input, mock_print):
        """_cmd_iniciar handles nonexistent timer gracefully."""
        interface = TerminalInterface()

        interface._cmd_iniciar()

        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "error" in call_args_str.lower() or "❌" in call_args_str


class TestCommandPause:
    """Tests for pause/resume timer command."""

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", return_value="test_timer")
    def test_cmd_pausar_pauses_running_timer(self, mock_input, mock_print):
        """_cmd_pausar pauses a running timer."""
        interface = TerminalInterface()
        interface.service.create_timer("test_timer", timedelta(minutes=5))
        interface.service.start_timer("test_timer")

        interface._cmd_pausar()

        timer = interface.service.get_timer("test_timer")
        assert timer.status == TimerStatus.PAUSED


class TestCommandReset:
    """Tests for reset timer command."""

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", return_value="test_timer")
    def test_cmd_resetar_resets_timer(self, mock_input, mock_print):
        """_cmd_resetar resets timer to original duration."""
        interface = TerminalInterface()
        original_duration = timedelta(minutes=5)
        interface.service.create_timer("test_timer", original_duration)
        interface.service.start_timer("test_timer")

        interface._cmd_resetar()

        timer = interface.service.get_timer("test_timer")
        assert timer.remaining == original_duration
        assert timer.status == TimerStatus.IDLE


class TestRunMethod:
    """Tests for main run loop."""

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", side_effect=["help", "exit"])
    def test_run_exits_on_exit_command(self, mock_input, mock_print):
        """run() exits when user enters 'exit'."""
        interface = TerminalInterface()

        interface.run()

        # Should exit cleanly after 'exit' command
        assert True  # If we reach here, run() exited properly

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", side_effect=["", "exit"])
    def test_run_handles_empty_input(self, mock_input, mock_print):
        """run() handles empty input gracefully."""
        interface = TerminalInterface()

        interface.run()

        # Should continue on empty input and exit on 'exit'
        assert True

    @patch("src.interfaces.terminal.interface.print")
    @patch("builtins.input", side_effect=["invalid_command", "exit"])
    def test_run_handles_unknown_command(self, mock_input, mock_print):
        """run() handles unknown commands gracefully."""
        interface = TerminalInterface()

        interface.run()

        call_args_str = " ".join(str(call) for call in mock_print.call_args_list)
        assert "unknown" in call_args_str.lower() or "❌" in call_args_str
