from datetime import timedelta
from typing import Dict
from src.core.timer import Timer


class TimerService:
    """Serviço de gerenciamento de timers.

    Responsável por criar, buscar e gerenciar timers. Não contém lógica
    de apresentação ou formatação - apenas operações nos timers.
    """

    def __init__(self):
        self._timers: Dict[str, Timer] = {}
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
        self._timers[name] = Timer(duration=duration)
        return self._timers[name]

    def list_timers(self) -> Dict[str, Timer]:
        """Retorna um dicionário com todos os timers ativos."""
        # Sempre retorna um dicionário (possivelmente vazio) para facilitar consumo em UIs
        return self._timers

    def start_timer(self, name: str) -> None:
        """Inicia um timer específico."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        timer.start_timer()

    def pause_or_resume_timer(self, name: str) -> None:
        """Pausa um timer específico."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        timer.pause_or_resume_timer()

    def reset_timer(self, name: str) -> None:
        """Reseta um timer para sua duração original."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        timer.reset_timer()

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
