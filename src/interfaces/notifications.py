from abc import ABC, abstractmethod


class NotificationService(ABC):
    @abstractmethod
    def on_timer_start(self, name: str): ...

    @abstractmethod
    def on_timer_end(self, name: str): ...
