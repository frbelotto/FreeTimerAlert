import threading
import time
from typing import Optional
from src.core.timer import Timer, TimerStatus
from src.services.logger import get_logger

logger = get_logger(__name__)


class TimerExecutor:
    """Executor responsável por gerenciar a execução em background de um Timer.
    
    Gerencia thread dedicada que executa o tick do timer a cada segundo.
    Permite iniciar, pausar e parar a execução do timer de forma thread-safe.
    """

    def __init__(self, timer: Timer, tick_interval: float = 1.0):
        """Inicializa o executor para um timer específico.
        
        Args:
            timer: Instância do Timer a ser executado
            tick_interval: Intervalo em segundos entre cada tick (padrão: 1.0)
        """
        self.timer = timer
        self.tick_interval = tick_interval
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> None:
        """Inicia a execução do timer em uma thread separada."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logger.warning("Executor já está em execução")
                return

            self._stop_event.clear()
            self.timer.start()
            
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            logger.info(f"Timer iniciado: {self.timer.duration}")

    def stop(self) -> None:
        """Para a execução do timer e encerra a thread."""
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                logger.warning("Executor não está em execução")
                return

            self._stop_event.set()
            self.timer.stop()
            
        # Aguarda thread terminar (fora do lock para evitar deadlock)
        if self._thread:
            self._thread.join(timeout=2.0)
            logger.info("Timer parado")

    def pause(self) -> None:
        """Pausa o timer (mantém thread ativa mas não executa ticks)."""
        self.timer.pause()
        logger.info("Timer pausado")

    def resume(self) -> None:
        """Resume o timer pausado."""
        self.timer.resume()
        logger.info("Timer retomado")

    def is_running(self) -> bool:
        """Verifica se o executor está ativo."""
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        """Loop principal de execução (roda na thread dedicada)."""
        try:
            while not self._stop_event.is_set():
                # Executa tick apenas se timer estiver RUNNING
                if self.timer.status == TimerStatus.RUNNING:
                    self.timer.tick(seconds=int(self.tick_interval))
                    
                    # Verifica se terminou
                    if self.timer.status == TimerStatus.FINISHED:
                        logger.info("Timer finalizado")
                        break
                
                # Aguarda próximo tick (verifica stop_event periodicamente)
                self._stop_event.wait(timeout=self.tick_interval)
                
        except Exception as e:
            logger.error(f"Erro na execução do timer: {e}", exc_info=True)
        finally:
            logger.debug("Thread do timer encerrada")

    def __enter__(self):
        """Suporte para context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que o timer seja parado ao sair do contexto."""
        self.stop()
        return False
