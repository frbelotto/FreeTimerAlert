from __future__ import annotations
from datetime import timedelta
from typing import Callable, List, Any
from enum import StrEnum, auto
from pydantic import BaseModel, Field, PrivateAttr, field_validator, ConfigDict
from src.services.logger import get_logger

logger = get_logger(__name__)


class TimerStatus(StrEnum):
    """Estados possíveis do timer."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    STOPPED = auto()


class Timer(BaseModel):
    """Timer - modelo de dados e lógica de contagem.
    
    Responsável apenas por gerenciar estado e executar contagem.
    A execução em background é gerenciada pelo TimerService.
    """
    
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

    @property
    def remaining(self) -> timedelta:
        """Retorna o tempo restante do timer."""
        return self._remaining
    
    @property
    def running(self) -> bool:
        """Indica se o timer está em execução."""
        return self.status == TimerStatus.RUNNING

    def start(self) -> None:
        """Marca o timer como iniciado."""
        if self.status not in (TimerStatus.RUNNING, TimerStatus.PAUSED):
            self.status = TimerStatus.RUNNING
            self._notify(self.on_start)

    def pause(self) -> None:
        """Pausa o timer."""
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED

    def resume(self) -> None:
        """Resume o timer pausado."""
        if self.status == TimerStatus.PAUSED:
            self.status = TimerStatus.RUNNING

    def stop(self) -> None:
        """Para o timer."""
        self.status = TimerStatus.STOPPED

    def reset(self) -> None:
        """Reseta o timer para duração original."""
        self._remaining = self.duration
        self.status = TimerStatus.IDLE

    def add_time(self, extra: timedelta) -> None:
        """Adiciona tempo extra ao timer."""
        self._remaining += extra

    def tick(self, seconds: int = 1) -> None:
        """Executa um tick de contagem.
        
        Args:
            seconds: Quantidade de segundos a decrementar
        """
        if self.status != TimerStatus.RUNNING:
            return
        
        self._remaining -= timedelta(seconds=seconds)
        
        if self._remaining <= timedelta(0):
            self._remaining = timedelta(0)
            self.status = TimerStatus.FINISHED
            self._notify(self.on_end)

    def _notify(self, callbacks: List[Callable[[Timer], None]]) -> None:
        """Notifica callbacks de forma segura."""
        for cb in callbacks:
            try:
                cb(self)
            except Exception as e:
                logger.error(f"Erro no callback: {e}")
