from abc import ABC, abstractmethod
from src.services.timer_service import TimerService


class TimerInterface(ABC):
    def __init__(self):
        self.service = TimerService()

    @abstractmethod
    def run(self) -> None:
        """Inicia a interface"""
        pass

    @abstractmethod
    def show_menu(self) -> None:
        """Exibe o menu da interface"""
        pass
