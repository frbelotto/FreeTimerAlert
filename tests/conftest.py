"""Configurações pytest para os testes do FreeTimer."""
import os
import pytest


@pytest.fixture(autouse=True)
def mute_audio():
    """Garante que o áudio está sempre em mute durante os testes."""
    os.environ["FREETIMER_MUTE"] = "1"
    yield


@pytest.fixture(autouse=True)
def suppress_timer_output(monkeypatch):
    """Suprime a saída do timer durante os testes para logs mais limpos."""
    import builtins
    original_print = builtins.print
    
    def mock_print(*args, **kwargs):
        # Só imprime se não for mensagem do timer
        msg = " ".join(str(arg) for arg in args)
        timer_prefixes = [
            "Tempo restante:",
            "⚠️ Timer já está em execução.",
            "▶️ Timer retomado.",
            "⏸️ Timer pausado.",
            "⏹️ Timer finalizado.",
            "⏱️ Timer iniciado.",
        ]
        if not any(msg.startswith(prefix) for prefix in timer_prefixes):
            original_print(*args, **kwargs)
    
    monkeypatch.setattr("builtins.print", mock_print)
