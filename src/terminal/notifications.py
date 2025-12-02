"""Sound notification functions for terminal interface."""

from pathlib import Path
from os import getenv
from src.services.logger import get_logger

logger = get_logger(__name__)

_current_sound = None


def get_sound_path(filename: str) -> Path:
    """Resolve absolute path for Assets/Sounds/<filename>.

    Args:
        filename: Sound file name.

    Returns:
        Absolute path to sound file.
    """
    base = Path(__file__).resolve().parents[2]  # .../FreeTimerAlert
    return base / "Assets" / "Sounds" / filename


def stop_current_sound() -> None:
    """Stop the currently playing sound if any."""
    global _current_sound
    if _current_sound:
        try:
            if hasattr(_current_sound, "stop"):
                _current_sound.stop()
        except Exception as e:
            logger.warning(f"⚠️  Failed to stop sound: {e}")
        finally:
            _current_sound = None


def play_sound(filename: str, block: bool = False) -> None:
    """Play sound file with error handling.

    Respects FREETIMER_MUTE environment variable to disable audio.
    Useful for testing and CI environments.

    Args:
        filename: Sound file name in Assets/Sounds directory.
        block: Whether to wait for sound to finish playing.
    """
    global _current_sound

    if getenv("FREETIMER_MUTE") == "1":
        logger.debug(f"🔇 (mute) Would play: {filename}")
        return

    # Stop any currently playing sound before starting a new one
    stop_current_sound()

    try:
        from playsound3 import playsound

        sound_path = str(get_sound_path(filename))
        _current_sound = playsound(sound_path, block=block)
    except Exception as e:
        logger.warning(f"⚠️  Failed to play sound '{filename}': {e}")


def play_start_sound() -> None:
    """Play timer start notification sound."""
    play_sound("clock-start.mp3", block=False)


def play_end_sound() -> None:
    """Play timer end notification sound."""
    play_sound("timer-terminer.mp3", block=True)
