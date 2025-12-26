"""System notification service for cross-platform OS notifications.

Provides desktop/system notifications for Windows, macOS, and Linux.
Automatically detects the operating system and uses appropriate backend.
"""

import os
import sys

from src.services.logger import get_logger

logger = get_logger(__name__)


def _is_wsl() -> bool:
    """Check if running in Windows Subsystem for Linux.

    Returns:
        True if running in WSL, False otherwise.
    """
    try:
        with open("/proc/version", "r") as f:
            return any(key in f.read().lower() for key in ("microsoft", "wsl"))
    except (FileNotFoundError, PermissionError):
        return False


def show_notification(title: str, message: str, timeout: int = 5000) -> None:
    """Display a system notification.

    Works on Windows, macOS, and Linux. Automatically selects the appropriate
    backend based on the operating system. Gracefully handles WSL environment.

    Args:
        title: Notification title.
        message: Notification message/body.
        timeout: Display duration in milliseconds (default: 5000ms = 5s).
                 Note: timeout is not guaranteed on all platforms.
    """
    # Skip notifications in WSL as D-Bus is usually unavailable
    if _is_wsl():
        logger.debug(f"WSL detected, skipping system notification: {title}")
        return

    try:
        if sys.platform == "win32":
            _show_windows_notification(title, message)
        elif sys.platform == "darwin":
            _show_macos_notification(title, message)
        else:  # Linux and others
            _show_linux_notification(title, message, timeout)
    except Exception as e:
        logger.debug(f"System notification not shown: {e}")


def _show_windows_notification(title: str, message: str) -> None:
    """Show notification on Windows using plyer.

    Args:
        title: Notification title.
        message: Notification message.
    """
    try:
        from plyer import notification

        notification.notify(title=title, message=message, app_name="FreeTimer", timeout=5)
        logger.debug(f"Windows notification shown: {title}")
    except Exception as e:
        logger.debug(f"Windows notification not available: {e}")


def _show_macos_notification(title: str, message: str) -> None:
    """Show notification on macOS using osascript.

    Args:
        title: Notification title.
        message: Notification message.
    """
    try:
        import subprocess

        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=False, timeout=5, capture_output=True)
        logger.debug(f"macOS notification shown: {title}")
    except Exception as e:
        logger.debug(f"macOS notification not available: {e}")


def _show_linux_notification(title: str, message: str, timeout: int = 5000) -> None:
    """Show notification on Linux using notify-send or plyer.

    Args:
        title: Notification title.
        message: Notification message.
        timeout: Display duration in milliseconds.
    """
    try:
        import subprocess

        # Tenta notify-send primeiro (mais comum no Linux)
        timeout_seconds = max(1, timeout // 1000)
        result = subprocess.run(
            ["notify-send", "-t", str(timeout), title, message],
            check=False,
            timeout=timeout_seconds + 1,
            capture_output=True,
        )
        if result.returncode == 0:
            logger.debug(f"Linux notify-send notification shown: {title}")
        else:
            raise subprocess.CalledProcessError(result.returncode, "notify-send")
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # Use plyer as fallback if notify-send is unavailable
        try:
            from plyer import notification

            notification.notify(title=title, message=message, app_name="FreeTimer", timeout=timeout // 1000)
            logger.debug(f"Linux plyer notification shown: {title}")
        except Exception as e:
            logger.debug(f"Linux notification not available: {e}")


def show_timer_finished_notification(timer_name: str) -> None:
    """Show a notification when a timer finishes.

    Args:
        timer_name: Name of the finished timer.
    """
    title = "Timer Finished!"
    message = f"Timer '{timer_name}' has finished."
    show_notification(title, message, timeout=10000)  # Show for 10 seconds
