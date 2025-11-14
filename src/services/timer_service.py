from datetime import timedelta
from typing import Dict
import threading
from src.core.timer import Timer, TimerStatus
from src.services.logger import get_logger

logger = get_logger(__name__)


class TimerService:
    """Serviço de gerenciamento e execução de timers.
    
    Responsável por:
    - Criar e armazenar timers
    - Gerenciar threads de execução
    - Controlar start/stop/pause de timers
    """

    def __init__(self):
        self._timers: Dict[str, Timer] = {}
        self._threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        
    def get_timer(self, name: str) -> Timer | None:
        """Busca um timer pelo nome."""
        return self._timers.get(name)

    def create_timer(self, name: str, duration: timedelta) -> Timer:
        """Cria um novo timer."""
        if name in self._timers:
            raise ValueError(f"Timer '{name}' já existe")
        
        timer = Timer(duration=duration)
        self._timers[name] = timer
        self._stop_events[name] = threading.Event()
        return timer

    def list_timers(self) -> Dict[str, Timer]:
        """Retorna todos os timers."""
        return self._timers

    def start_timer(self, name: str) -> None:
        """Inicia a execução de um timer em background."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        
        with self._lock:
            # Verifica se já está rodando
            if name in self._threads and self._threads[name].is_alive():
                logger.warning(f"Timer '{name}' já está em execução")
                return
            
            # Prepara para iniciar
            self._stop_events[name].clear()
            timer.start()
            
            # Cria e inicia thread
            thread = threading.Thread(target=self._run_timer, args=(name,), daemon=True)
            self._threads[name] = thread
            thread.start()
            logger.info(f"Timer '{name}' iniciado: {timer.duration}")

    def stop_timer(self, name: str) -> None:
        """Para completamente um timer."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        
        with self._lock:
            if name not in self._threads or not self._threads[name].is_alive():
                logger.warning(f"Timer '{name}' não está em execução")
                return
            
            # Sinaliza para parar
            self._stop_events[name].set()
            timer.stop()
        
        # Aguarda thread terminar
        if name in self._threads:
            self._threads[name].join(timeout=2.0)
            logger.info(f"Timer '{name}' parado")

    def pause_or_resume_timer(self, name: str) -> None:
        """Pausa ou retoma um timer."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        
        if timer.status == TimerStatus.PAUSED:
            timer.resume()
            logger.info(f"Timer '{name}' retomado")
        else:
            timer.pause()
            logger.info(f"Timer '{name}' pausado")

    def reset_timer(self, name: str) -> None:
        """Reseta um timer para duração original."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        
        # Para se estiver rodando
        if name in self._threads and self._threads[name].is_alive():
            self.stop_timer(name)
        
        timer.reset()
        logger.info(f"Timer '{name}' resetado")

    def add_time(self, name: str, duration: timedelta) -> None:
        """Adiciona tempo extra a um timer."""
        timer = self.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não existe")
        
        timer.add_time(duration)
        logger.info(f"Adicionado {duration} ao timer '{name}'")

    def _run_timer(self, name: str) -> None:
        """Loop de execução de um timer (roda em thread dedicada)."""
        timer = self._timers[name]
        stop_event = self._stop_events[name]
        
        try:
            while not stop_event.is_set():
                if timer.status == TimerStatus.RUNNING:
                    timer.tick(seconds=1)
                    
                    if timer.status == TimerStatus.FINISHED:
                        logger.info(f"Timer '{name}' finalizado")
                        break
                
                # Aguarda 1 segundo
                stop_event.wait(timeout=1.0)
                
        except Exception as e:
            logger.error(f"Erro na execução do timer '{name}': {e}", exc_info=True)
        finally:
            logger.debug(f"Thread do timer '{name}' encerrada")

    @property
    def available_services(self):
        """Retorna os serviços disponíveis."""
        return {
            "Criar : Criar timers (nome, duração)": self.create_timer,
            "Listar : Listar timers": self.list_timers,
            "Iniciar : Iniciar timer (name)": self.start_timer,
            "Pausar : Pausar ou resumir timer (nome)": self.pause_or_resume_timer,
            "Resetar : Resetar um timer (nome)": self.reset_timer,
            "Adicionar : Adicionar tempo extra a um timer (nome, duração)": self.add_time,
        }
