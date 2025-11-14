import pytest
import time
from datetime import timedelta
from src.core.timer import Timer, TimerStatus


def test_timer_with_background_execution():
    """Testa criação do timer com execução automática."""
    timer = Timer(duration=timedelta(seconds=5))
    
    assert timer.duration == timedelta(seconds=5)
    assert timer.tick_interval == timedelta(seconds=1)
    assert not timer.is_active


def test_timer_start_stop():
    """Testa start e stop do timer."""
    timer = Timer(duration=timedelta(seconds=5))
    
    timer.start()
    assert timer.is_active
    assert timer.status == TimerStatus.RUNNING
    
    time.sleep(0.5)  # Aguarda thread iniciar
    
    timer.stop()
    time.sleep(0.5)  # Aguarda thread terminar
    assert not timer.is_active
    assert timer.status == TimerStatus.STOPPED


def test_timer_automatic_tick():
    """Testa que o timer faz tick automático em background."""
    timer = Timer(duration=timedelta(seconds=3), tick_interval=timedelta(seconds=1))
    
    timer.start()
    time.sleep(2.2)  # Aguarda ~2 ticks
    
    # Deve ter decrementado aproximadamente 2 segundos
    assert timer.remaining <= timedelta(seconds=1)
    assert timer.remaining >= timedelta(seconds=0)
    
    timer.stop()


def test_timer_finish():
    """Testa que o timer detecta finalização automaticamente."""
    finished = []
    
    def on_end(t: Timer):
        finished.append(True)
    
    timer = Timer(duration=timedelta(seconds=2), on_end=[on_end])
    
    timer.start()
    time.sleep(2.5)  # Aguarda finalizar
    
    assert timer.status == TimerStatus.FINISHED
    assert len(finished) == 1
    assert not timer.is_active  # Thread deve ter encerrado


def test_timer_pause_resume():
    """Testa pause e resume do timer."""
    timer = Timer(duration=timedelta(seconds=10))
    
    timer.start()
    time.sleep(1.2)  # ~1 tick
    
    timer.pause()
    assert timer.status == TimerStatus.PAUSED
    remaining_at_pause = timer.remaining
    
    time.sleep(1.5)  # Durante pause não deve decrementar
    assert timer.remaining == remaining_at_pause
    
    timer.resume()
    assert timer.status == TimerStatus.RUNNING
    time.sleep(1.2)  # Deve voltar a decrementar
    assert timer.remaining < remaining_at_pause
    
    timer.stop()


def test_timer_context_manager():
    """Testa uso do timer como context manager."""
    timer = Timer(duration=timedelta(seconds=5))
    
    with timer:
        assert timer.is_active
        time.sleep(0.5)
    
    # Deve ter parado ao sair do contexto
    assert not timer.is_active


def test_multiple_timers():
    """Testa que múltiplos timers funcionam independentemente."""
    timer1 = Timer(duration=timedelta(seconds=3))
    timer2 = Timer(duration=timedelta(seconds=5))
    
    timer1.start()
    timer2.start()
    
    assert timer1.is_active
    assert timer2.is_active
    
    time.sleep(1.2)
    
    # Ambos devem estar decrementando
    assert timer1.remaining < timedelta(seconds=3)
    assert timer2.remaining < timedelta(seconds=5)
    
    timer1.stop()
    timer2.stop()


def test_timer_double_start():
    """Testa que não permite start duplo."""
    timer = Timer(duration=timedelta(seconds=5))
    
    timer.start()
    timer.start()  # Não deve criar segunda thread
    
    assert timer.is_active
    timer.stop()


def test_timer_stop_not_running():
    """Testa stop quando não está rodando."""
    timer = Timer(duration=timedelta(seconds=5))
    
    timer.stop()  # Não deve dar erro
    assert not timer.is_active


def test_timer_reset():
    """Testa reset do timer."""
    timer = Timer(duration=timedelta(seconds=10))
    
    timer.start()
    time.sleep(1.2)
    timer.stop()
    
    # Remaining deve ter decrementado
    assert timer.remaining < timedelta(seconds=10)
    
    # Após reset deve voltar ao valor original
    timer.reset()
    assert timer.remaining == timedelta(seconds=10)
    assert timer.status == TimerStatus.IDLE