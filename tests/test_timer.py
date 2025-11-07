import time
from datetime import timedelta

from src.core.timer import Timer


def test_timer_events_start_end():
    """Verifica que os callbacks on_start e on_end são chamados na ordem correta."""
    events = []

    def on_start(_):
        events.append("start")

    def on_end(_):
        events.append("end")

    t = Timer(duration=timedelta(seconds=1))
    t.on_start = [on_start]
    t.on_end = [on_end]

    t.start_timer()
    # Poll for timer completion with a timeout
    timeout = 3  # seconds
    start_time = time.time()
    while t.running and (time.time() - start_time) < timeout:
        time.sleep(0.05)
    
    assert events == ["start", "end"]


def test_terminal_notification_mute():
    """Verifica que o modo mute funciona e não levanta exceções."""
    # Import lazily to pick up env var
    from src.interfaces.terminal.terminal_notification import TerminalNotificationService

    svc = TerminalNotificationService()
    # Should not raise when muted
    svc.on_timer_start("unit")
    svc.on_timer_end("unit")


def test_timer_pause_resume():
    """Verifica que o timer pode ser pausado e retomado."""
    t = Timer(duration=timedelta(seconds=5))
    t.start_timer()
    time.sleep(1.5)
    
    # Pausa
    t.pause_or_resume_timer()
    assert not t.running
    remaining_at_pause = t.remaining
    assert remaining_at_pause is not None
    
    time.sleep(1)
    # Tempo não deve ter mudado durante a pausa (tolera 1s de diferença por race condition)
    assert t.remaining is not None
    diff = abs((t.remaining - remaining_at_pause).total_seconds())
    assert diff <= 1, f"Timer mudou {diff}s durante pausa"
    
    # Retoma
    t.pause_or_resume_timer()
    assert t.running
    time.sleep(1.5)
    
    # Tempo deve ter diminuído após retomar
    assert t.remaining is not None
    assert t.remaining < remaining_at_pause
    
    # Cleanup: para o timer
    t.reset_timer()


def test_timer_reset():
    """Verifica que o reset interrompe e restaura o timer."""
    t = Timer(duration=timedelta(seconds=5))
    t.start_timer()
    time.sleep(1)
    
    # Reset deve parar e restaurar
    t.reset_timer()
    # Aguarda thread finalizar
    timeout = 3  # segundos
    start_time = time.time()
    while t.running and (time.time() - start_time) < timeout:
        time.sleep(0.05)
    
    assert not t.running
    assert t.remaining == timedelta(seconds=5)


def test_timer_add_time():
    """Verifica que é possível adicionar tempo ao timer."""
    t = Timer(duration=timedelta(seconds=5))
    t.start_timer()
    time.sleep(1)
    
    # Pause the timer to avoid race condition
    t.pause_or_resume_timer()
    remaining_before = t.remaining
    assert remaining_before is not None
    
    # Primeira adição de 3 segundos
    t.add_time(timedelta(seconds=3))
    assert t.remaining == remaining_before + timedelta(seconds=3)
    
    # Segunda adição de 3 segundos (acumula sobre o valor atual)
    remaining_after_first = t.remaining
    assert remaining_after_first is not None
    t.add_time(timedelta(seconds=3))
    assert t.remaining == remaining_after_first + timedelta(seconds=3)
    
    # Cleanup: para o timer
    t.reset_timer()
