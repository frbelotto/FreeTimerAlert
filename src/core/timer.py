from __future__ import annotations
from datetime import timedelta
from typing import Callable, List
from enum import StrEnum, auto
from pydantic import BaseModel, Field, PrivateAttr, field_validator, ConfigDict
from src.services.logger import get_logger

logger = get_logger(__name__)

class TimerStatus(StrEnum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    STOPPED = auto()


class Timer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    duration: timedelta
    status: TimerStatus = Field(default=TimerStatus.IDLE)
    on_start: List[Callable[[Timer], None]] = Field(default_factory=list)
    on_end: List[Callable[[Timer], None]] = Field(default_factory=list)
    
    _remaining: timedelta = PrivateAttr()
 
    def model_post_init(self, __context: Any) -> None:
        self._remaining = self.duration

    @field_validator("duration")
    def validate_positive(cls, duration: timedelta):
        if duration <= timedelta(0):
            raise ValueError("duration must be > 0")
        return duration

    def start(self):
        if self.status in (TimerStatus.RUNNING, TimerStatus.PAUSED):
            return
        self.status = TimerStatus.RUNNING
        self._notify(self.on_start)

    def pause(self):
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED

    def resume(self):
        if self.status == TimerStatus.PAUSED:
            self.status = TimerStatus.RUNNING

    def tick(self, seconds: int = 1):
        if self.status != TimerStatus.RUNNING:
            return
        self._remaining -= timedelta(seconds=seconds)
        if self._remaining <= timedelta(0):
            self._remaining = timedelta(0)
            self.status = TimerStatus.FINISHED
            self._notify(self.on_end)

    def add_time(self, extra: timedelta):
        self._remaining += extra

    def reset(self):
        self._remaining = self.duration
        self.status = TimerStatus.IDLE

    def stop(self):
        self.status = TimerStatus.STOPPED
        self._remaining = self.duration

    def _notify(self, callbacks: List[Callable[[Timer], None]]):
        for cb in callbacks:
            try:
                cb(self)
            except Exception as e:
                logger.error(f"Erro no callback: {e}")
