from datetime import timedelta
from typing import Dict
from src.core.timer import Timer
from src.core.timerexecutor import TimerExecutor


class TimerService:
    """Serviço de gerenciamento de timers.

    Responsável por criar, buscar e gerenciar timers e seus executores.
    Não contém lógica de apresentação ou formatação - apenas operações nos timers.
    """

    def __init__(self):
        self._timers: Dict[str, Timer] = {}
        self._executors: Dict[str, TimerExecutor] = {}
        self._listservices = {
            "Criar : Criar timers (nome, duração)": self.create_timer,
            "Listar : Listar timers": self.list_timers,
            "Iniciar : Iniciar timer (name)": self.start_timer,
            "Pausar : Pausar ou resumir timer (nome)": self.pause_or_resume_timer,
            "Resetar : Resetar um timer (nome)": self.reset_timer,
            "Adicionar : Adicionar tempo extra a um timer (nome, duração)": self.add_time,
        }

    def get_timer(self, name: str) -> Timer | None:
        """Busca um timer pelo nome."""
        return self._timers.get(name)

    def create_timer(self, name: str, duration: timedelta) -> Timer:
        """Cria um novo timer com a duração especificada."""
        if name in self._timers:
            raise ValueError(f"Timer '{name}' já existe")
        timer = Timer(duration=duration)
        self._timers[name] = timer
        self._executors[name] = TimerExecutor(timer)
        return timer

    def list_timers(self) -> Dict[str, Timer]:
        """Retorna um dicionário com todos os timers ativos."""
        # Sempre retorna um dicionário (possivelmente vazio) para facilitar consumo em UIs
        return self._timers

    def start_timer(self, name: str) -> None:
        """Inicia um timer específico."""
        executor = self._executors.get(name)
        if not executor:
            raise ValueError(f"Timer '{name}' não existe")
        executor.start()

    def pause_or_resume_timer(self, name: str) -> None:
        """Pausa ou retoma um timer específico."""
        executor = self._executors.get(name)
        if not executor:
            raise ValueError(f"Timer '{name}' não existe")
        timer = self.get_timer(name)
        if timer and timer.status.value == "paused":
            executor.resume()
        else:
            executor.pause()

    def reset_timer(self, name: str) -> None:
        """Reseta um timer para sua duração original."""
        executor = self._executors.get(name)
        timer = self.get_timer(name)
        if not timer or not executor:
            raise ValueError(f"Timer '{name}' não existe")
        executor.stop()
        timer.reset()

    def add_time(self, name: str, duration: timedelta) -> None:
        """Adiciona tempo extra a um timer existente."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        timer.add_time(duration)

    @property
    def available_services(self):
        """Retorna o dicionário de serviços disponíveis."""
        return self._listservices
