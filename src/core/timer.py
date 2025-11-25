from __future__ import annotations
from datetime import timedelta
import time
from typing import Callable, Any
from enum import StrEnum, auto
import threading
from pydantic import BaseModel, Field, PrivateAttr, field_validator, ConfigDict
from src.services.logger import get_logger

logger = get_logger(__name__)


class TimerStatus(StrEnum):
    """Possible timer states.

    IDLE: Timer is created or reset and not yet started.
    RUNNING: Countdown is actively decrementing.
    PAUSED: Countdown is temporarily halted (thread still alive).
    FINISHED: Countdown reached zero naturally.
    STOPPED: Timer was manually stopped before finishing or due to error.
    """
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    STOPPED = auto()


class Timer(BaseModel):
    """Thread-based countdown timer.

    Manages its own background thread. Once started it decrements the remaining
    time every second until it reaches zero (FINISHED) or is manually stopped
    (STOPPED). Thread-safe operations are guarded by an internal lock. Callbacks
    may be provided for start and natural end events.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    duration: timedelta
    status: TimerStatus = Field(default=TimerStatus.IDLE)
    on_start: list[Callable[[Timer], None]] = Field(default_factory=list)
    on_end: list[Callable[[Timer], None]] = Field(default_factory=list)
    
    _remaining: timedelta = PrivateAttr()  # Remaining timer time (continuously updated)
    _thread: threading.Thread | None = PrivateAttr(default=None)  # Background thread that executes the timer loop
    _stop_event: threading.Event = PrivateAttr(default_factory=threading.Event)  # Thread-safe flag: main thread sets it → background thread reads it and stops gracefully
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)  # Lock to guarantee thread-safety when accessing/modifying _remaining
    _last_update_monotonic: float = PrivateAttr(default=0.0)  # Last update timestamp (time.monotonic() is not affected by OS clock adjustments)
    _resolution_seconds: float = PrivateAttr(default=0.1)  # Loop interval: controls precision vs CPU usage (0.1s = 10 updates/second)
 
    def model_post_init(self, __context: Any) -> None:
        """Initialize private attributes after model construction."""
        self._remaining = self.duration

    @field_validator("duration")
    def validate_positive(cls, duration: timedelta) -> timedelta:
        """Validate that initial duration is strictly positive."""
        if duration <= timedelta(0):
            raise ValueError("duration must be > 0")
        return duration

    @property
    def remaining(self) -> timedelta:
        """Return remaining countdown time."""
        with self._lock:  # Acquires lock before reading _remaining (ensures thread is not modifying simultaneously)
            return self._remaining
    
    @property
    def running(self) -> bool:
        """Return True if the timer is actively running."""
        return self.status == TimerStatus.RUNNING
    
    @property
    def is_active(self) -> bool:
        """Check if the internal execution thread is alive."""
        with self._lock:  # Lock protects access to _thread (another thread might be modifying it)
            return self._thread is not None and self._thread.is_alive()

    def get_progress(self) -> float:
        """Return progress fraction (0.0 - 1.0).

        Returns:
            Fraction of elapsed time relative to the original duration.
        """
        with self._lock:  # Lock required for atomic read of _remaining (avoids reading partially updated value)
            elapsed = self.duration - self._remaining
        return max(0.0, min(1.0, elapsed.total_seconds() / self.duration.total_seconds()))

    def start(self) -> None:
        """Start the timer and spawn its background thread.

        Safe to call multiple times; subsequent calls while already running
        have no effect.
        """
        with self._lock:  # Lock protects entire critical section of initialization
            if self._thread is not None and self._thread.is_alive():
                logger.warning("Timer already running")
                return
            if self.status in (TimerStatus.RUNNING, TimerStatus.PAUSED):
                return
            # CRITICAL: Resets Event to False (unset state) to allow thread to run
            # Without this, if timer was stopped before (Event=True), the new thread would exit immediately
            # because while not self._stop_event.is_set() would be False from the start
            self._stop_event.clear()
            self.status = TimerStatus.RUNNING
            self._last_update_monotonic = time.monotonic()  # Marks initial time using monotonic clock (not affected by system time changes)
            callbacks = list(self.on_start)
            self._thread = threading.Thread(target=self._run, daemon=True)  # daemon=True: thread terminates automatically when main program ends
            self._thread.start()  # Starts thread execution in background (calls _run() in parallel)
        # Callbacks executed OUTSIDE lock to avoid deadlock (callback might try to acquire same lock)
        self._notify(callbacks)
        logger.info(f"Timer started: duration={self.duration}")

    def pause(self) -> None:
        """Pause the countdown (thread keeps alive)."""
        # Acquire lock to ensure status transition is not concurrent with _run() reading/updating timing internals
        with self._lock:
            if self.status == TimerStatus.RUNNING:
                self.status = TimerStatus.PAUSED
                logger.info("Timer paused")

    def resume(self) -> None:
        """Resume a previously paused timer."""
        # Protected by lock to avoid race with _run() loop computing delta while we reset reference clock
        with self._lock:
            if self.status == TimerStatus.PAUSED:
                self.status = TimerStatus.RUNNING
                # CRITICAL: Updates _last_update_monotonic to prevent next delta from being huge
                # (without this, the paused time would be subtracted from remaining all at once)
                self._last_update_monotonic = time.monotonic()
                logger.info("Timer resumed")

    def stop(self) -> None:
        """Stop the timer and join its thread if active."""
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                logger.warning("Timer not running")
                return
            # INTER-THREAD COMMUNICATION: Main thread sets Event to True (signals stop)
            # Background thread (in _run loop) checks is_set() or wait() detects it and exits gracefully
            # This is thread-safe communication mechanism (no lock needed for Event itself)
            self._stop_event.set()
            self.status = TimerStatus.STOPPED
            thread = self._thread  # Copies reference to use outside lock
        if thread:
            thread.join(timeout=2.0)  # Waits for thread to finish (outside lock to not block other operations)
            logger.info("Timer stopped")

    def reset(self) -> None:
        """Reset timer to its original duration and IDLE state.

        If running, it is stopped first.
        """
        was_active = self.is_active
        if was_active:
            self.stop()
        with self._lock:
            self._remaining = self.duration
            self.status = TimerStatus.IDLE
            self._last_update_monotonic = 0.0
        logger.info("Timer reset")

    def add_time(self, extra: timedelta) -> None:
        """Add extra time to the timer.

        Args:
            extra: Positive timedelta to be added.
        """
        if extra <= timedelta(0):
            logger.warning("Extra time must be positive; ignored")
            return
        with self._lock:
            self._remaining += extra
        logger.info(f"Extra time added: {extra}")

    def tick(self, seconds: int = 1) -> None:
        """Perform a tick decrementing remaining time.

        Args:
            seconds: Number of seconds to subtract.
        """
        if self.status != TimerStatus.RUNNING:
            return
        finished_callbacks: list[Callable[[Timer], None]] | None = None
        with self._lock:  # Lock ensures _remaining modification is atomic
            self._remaining -= timedelta(seconds=seconds)
            if self._remaining <= timedelta(0):
                self._remaining = timedelta(0)
                self.status = TimerStatus.FINISHED
                finished_callbacks = list(self.on_end)  # Copies callbacks inside lock
        if finished_callbacks is not None:  # Executes callbacks OUTSIDE lock
            self._notify(finished_callbacks)

    def _run(self) -> None:
        """Internal background loop executed by the thread."""
        try:
            # LOOP CONTROL: Checks if Event is set (True). If set, exits loop (not True = False)
            # Main thread can set Event at any time via stop(), and this thread will detect it
            while not self._stop_event.is_set():
                callbacks: list[Callable[[Timer], None]] | None = None
                if self.status == TimerStatus.RUNNING:
                    now = time.monotonic()  # Captures current time (monotonic - doesn't regress even if system time changes)
                    with self._lock:  # Critical section: multiple variables being read/modified atomically
                        delta = now - self._last_update_monotonic  # Calculates how much time passed since last update
                        if delta >= self._resolution_seconds:  # Only updates if enough time passed (controls precision)
                            self._last_update_monotonic = now  # Updates time reference
                            self._remaining -= timedelta(seconds=delta)  # Subtracts elapsed time from remaining
                            if self._remaining <= timedelta(0):
                                self._remaining = timedelta(0)
                                self.status = TimerStatus.FINISHED
                                callbacks = list(self.on_end)
                    if self.status == TimerStatus.FINISHED:  # Checks outside lock (status might have changed)
                        if callbacks:
                            self._notify(callbacks)  # Callbacks executed outside lock
                        logger.info("Timer finished")
                        break
                    # EVENT.WAIT() MECHANISM:
                    # 1. Blocks thread for timeout duration (0.1s) - acts as sleep
                    # 2. BUT if _stop_event.set() is called by another thread during this time,
                    #    wait() returns immediately (True) instead of waiting full timeout
                    # 3. Returns True if Event was set, False if timeout elapsed
                    # This is MORE EFFICIENT than: time.sleep(0.1) + checking is_set() in loop
                    # because it responds IMMEDIATELY to stop signal instead of waiting for sleep to end
                    if self._stop_event.wait(timeout=self._resolution_seconds):
                        break  # Event was set (stop requested) → exit loop
                else:
                    # Timer paused/idle: same wait() mechanism maintains responsiveness to stop()
                    # without consuming CPU in busy-wait loop
                    if self._stop_event.wait(timeout=self._resolution_seconds):
                        break  # Event was set (stop requested) → exit loop
        except Exception as e:
            logger.error(f"Timer execution error: {e}", exc_info=True)
            self.status = TimerStatus.STOPPED
        finally:
            logger.debug("Timer thread terminated")

    def _notify(self, callbacks: list[Callable[[Timer], None]]) -> None:
        """Safely execute callbacks.

        Exceptions inside callbacks are logged and do not stop timer execution.
        """
        for cb in callbacks:
            try:
                cb(self)
            except Exception as e:
                logger.error(f"Callback error: {e}")
