from datetime import timedelta
from typing import Dict, Callable
from src.core.timer import Timer, TimerStatus
from src.services.logger import get_logger

logger = get_logger(__name__)


class TimerService:
    """Timer management service.

    Coordinates multiple named timers.
    Each timer manages its own execution.
    """

    def __init__(self):
        self._timers: Dict[str, Timer] = {}

    def get_timer(self, name: str) -> Timer | None:
        """Retrieve a timer by name.

        Args:
            name: Timer identifier.

        Returns:
            Timer instance or None if not found.
        """
        return self._timers.get(name)

    def create_timer(self, name: str, duration: timedelta, on_start: list[Callable[[Timer], None]] | None = None, on_end: list[Callable[[Timer], None]] | None = None) -> Timer:
        """Create a new timer.

        Args:
            name: Unique identifier for the timer.
            duration: Timer duration.
            on_start: Optional list of callbacks to execute when timer starts.
            on_end: Optional list of callbacks to execute when timer ends.

        Returns:
            Created Timer instance.

        Raises:
            ValueError: If timer name already exists.
        """
        if name in self._timers:
            logger.error(f"Timer '{name}' already exists")
            raise ValueError(f"Timer '{name}' already exists")

        timer = Timer(duration=duration, on_start=on_start or [], on_end=on_end or [])
        self._timers[name] = timer
        logger.info(f"Timer '{name}' created with duration {duration}")
        return timer

    def list_timers(self) -> Dict[str, Timer]:
        """Return all timers.

        Returns:
            Dictionary mapping timer names to Timer instances.
        """
        return self._timers

    def start_timer(self, name: str) -> None:
        """Start timer execution.

        Args:
            name: Timer identifier.

        Raises:
            ValueError: If timer does not exist.
        """
        timer = self.get_timer(name)
        if not timer:
            logger.error(f"Cannot start: timer '{name}' does not exist")
            raise ValueError(f"Timer '{name}' does not exist")
        timer.start()
        logger.debug(f"Start command issued for timer '{name}'")

    def stop_timer(self, name: str) -> None:
        """Completely stop a timer.

        Args:
            name: Timer identifier.

        Raises:
            ValueError: If timer does not exist.
        """
        timer = self.get_timer(name)
        if not timer:
            logger.error(f"Cannot stop: timer '{name}' does not exist")
            raise ValueError(f"Timer '{name}' does not exist")
        timer.stop()
        logger.debug(f"Stop command issued for timer '{name}'")

    def pause_or_resume_timer(self, name: str) -> None:
        """Pause or resume a timer.

        Args:
            name: Timer identifier.

        Raises:
            ValueError: If timer does not exist.
        """
        timer = self.get_timer(name)
        if not timer:
            logger.error(f"Cannot pause/resume: timer '{name}' does not exist")
            raise ValueError(f"Timer '{name}' does not exist")

        if timer.status == TimerStatus.PAUSED:
            timer.resume()
            logger.debug(f"Resume command issued for timer '{name}'")
        else:
            timer.pause()
            logger.debug(f"Pause command issued for timer '{name}'")

    def reset_timer(self, name: str) -> None:
        """Reset a timer to its original duration.

        Args:
            name: Timer identifier.

        Raises:
            ValueError: If timer does not exist.
        """
        timer = self.get_timer(name)
        if not timer:
            logger.error(f"Cannot reset: timer '{name}' does not exist")
            raise ValueError(f"Timer '{name}' does not exist")
        timer.reset()
        logger.debug(f"Reset command issued for timer '{name}'")

    def add_time(self, name: str, duration: timedelta) -> None:
        """Add extra time to a timer.

        Args:
            name: Timer identifier.
            duration: Extra time to add.

        Raises:
            ValueError: If timer does not exist.
        """
        timer = self.get_timer(name)
        if not timer:
            logger.error(f"Cannot add time: timer '{name}' does not exist")
            raise ValueError(f"Timer '{name}' does not exist")
        timer.add_time(duration)
        logger.debug(f"Added {duration} to timer '{name}'")

    def remove_timer(self, name: str) -> None:
        """Remove timer from catalog.

        Only allows removal of finished or stopped timers for safety.

        Args:
            name: Timer identifier.

        Raises:
            ValueError: If timer does not exist or is still active.
        """
        timer = self.get_timer(name)
        if not timer:
            logger.error(f"Cannot remove: timer '{name}' does not exist")
            raise ValueError(f"Timer '{name}' does not exist")

        if timer.status not in (TimerStatus.FINISHED, TimerStatus.STOPPED, TimerStatus.IDLE):
            logger.error(f"Cannot remove active timer '{name}'")
            raise ValueError(f"Timer '{name}' is still active. Stop it before removing.")

        del self._timers[name]
        logger.info(f"Timer '{name}' removed from catalog")
