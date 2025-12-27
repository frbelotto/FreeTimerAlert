"""Tests for terminal notifications and sound handling."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.interfaces.terminal import notifications


class TestNotifications:
    """Test suite for sound notification logic."""

    def test_get_sound_path_structure(self):
        """Ensure sound path resolution points to Assets/Sounds folder."""
        path = notifications.get_sound_path("test.mp3")
        # Check that the path ends with Assets/Sounds/test.mp3
        assert path.name == "test.mp3"
        assert path.parent.name == "Sounds"
        assert path.parent.parent.name == "Assets"

    def test_play_sound_calls_library(self):
        """Test that play_sound calls playsound3 when not muted."""
        # We mock the module 'playsound3' because it's imported inside the function
        with patch.dict(os.environ, {}, clear=True):  # Ensure FREETIMER_MUTE is not set
            # Since playsound is imported inside the function from playsound3,
            # we patch the library function directly.
            with patch("playsound3.playsound") as mock_lib_play:
                notifications.play_sound("test.mp3")
                mock_lib_play.assert_called_once()

                # Verify the path passed contains the filename
                args, _ = mock_lib_play.call_args
                assert "test.mp3" in str(args[0])

    def test_mute_environment_variable(self):
        """Test that FREETIMER_MUTE=1 prevents sound playback."""
        with patch.dict(os.environ, {"FREETIMER_MUTE": "1"}):
            with patch("playsound3.playsound") as mock_play:
                notifications.play_sound("test.mp3")
                mock_play.assert_not_called()

    def test_play_sound_handles_exception(self):
        """Test that exceptions during playback are caught and logged."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("playsound3.playsound", side_effect=Exception("Audio device error")):
                # Should not raise exception, just log warning
                try:
                    notifications.play_sound("test.mp3")
                except Exception as e:
                    pytest.fail(f"play_sound raised exception unexpectedly: {e}")

    def test_stop_current_sound(self):
        """Test that stop_current_sound calls stop on the active sound object."""
        mock_sound_obj = MagicMock()

        # Inject our mock sound object into the module's global state
        notifications._current_sound = mock_sound_obj

        notifications.stop_current_sound()

        mock_sound_obj.stop.assert_called_once()
        assert notifications._current_sound is None

    def test_required_sound_files_exist(self):
        """Verify that the sound files used in code actually exist on disk."""
        # This ensures we don't ship code referencing missing assets
        required_sounds = ["clock-start.mp3", "timer-terminer.mp3"]

        for filename in required_sounds:
            path = notifications.get_sound_path(filename)
            assert path.exists(), f"Required sound asset missing: {filename}"
            assert path.is_file(), f"Sound asset is not a file: {filename}"
