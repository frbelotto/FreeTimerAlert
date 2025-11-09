from playsound3 import playsound
from pathlib import Path
from os import getenv
from src.interfaces.notifications import NotificationService
from src.services.logger import get_logger

logger = get_logger(__name__)


def _sound_path(filename: str) -> str:
    """Resolve o caminho absoluto para Assets/Sounds/<filename>."""
    base = Path(__file__).resolve().parents[3]  # .../FreeTimer
    return str(base / "Assets" / "Sounds" / filename)


def _play_sound(filename: str):
    """Toca um som e retorna o objeto de reprodução quando disponível.

    - Respeita a variável de ambiente FREETIMER_MUTE=1 para desabilitar áudio (útil em testes/CI).
    - Captura e silencia erros de backend de áudio, retornando None.
    """
    if getenv("FREETIMER_MUTE") == "1":
        logger.debug(f"🔇 (mute) Tocaria: {filename}")
        return None
    try:
        return playsound(_sound_path(filename), block=False)
    except Exception as e:
        logger.warning(f"⚠️  Falha ao reproduzir som '{filename}': {e}")
        return None


class TerminalNotificationService(NotificationService):
    def on_timer_start(self, name: str):
        logger.info(f"🟢 Timer '{name}' foi iniciado!")
        _play_sound("clock-start.mp3")

    def on_timer_end(self, name: str):
        logger.info(f"⏰ Timer '{name}' foi concluído!")
        _play_sound("timer-terminer.mp3")
