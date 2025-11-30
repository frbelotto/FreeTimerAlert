"""Testes para o módulo logger.

Este módulo testa:
- Singleton pattern do LoggerService
- Configuração correta do logger
- Função get_logger retorna logging.Logger
- Métodos de logging (.info, .error, .warning, .debug) funcionam
"""

import logging
from io import StringIO

import pytest

from src.services.logger import LoggerService, get_logger


class TestLoggerService:
    """Testes para a classe LoggerService (singleton)."""

    def test_singleton_pattern(self):
        """Verifica que LoggerService é um singleton."""
        instance1 = LoggerService()
        instance2 = LoggerService()
        assert instance1 is instance2

    def test_logger_setup_is_called(self):
        """Verifica que o setup do logger é executado na criação."""
        # Força nova instância (limpa o singleton para teste)
        LoggerService._instance = None

        instance = LoggerService()
        root_logger = logging.getLogger()

        # Verifica que há pelo menos um handler
        assert len(root_logger.handlers) > 0

        # Verifica o nível configurado
        assert root_logger.level == logging.INFO

    def test_logger_has_stream_handler(self):
        """Verifica que o logger tem um StreamHandler configurado."""
        LoggerService._instance = None
        instance = LoggerService()

        root_logger = logging.getLogger()
        handlers = root_logger.handlers

        # Verifica que há um StreamHandler
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)

    def test_formatter_is_configured(self):
        """Verifica que o formatter está configurado."""
        LoggerService._instance = None
        instance = LoggerService()

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]

        # Verifica que o handler tem formatter
        assert handler.formatter is not None


class TestGetLogger:
    """Testes para a função get_logger."""

    def test_get_logger_returns_logger_instance(self):
        """Verifica que get_logger retorna uma instância de logging.Logger."""
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_different_names(self):
        """Verifica que get_logger retorna loggers diferentes para nomes diferentes."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2

    def test_get_logger_same_name_returns_same_instance(self):
        """Verifica que get_logger retorna a mesma instância para o mesmo nome."""
        logger1 = get_logger("test")
        logger2 = get_logger("test")

        assert logger1 is logger2


class TestLoggerMethods:
    """Testes para verificar que os métodos de logging funcionam."""

    @pytest.fixture(autouse=True)
    def setup_logger(self):
        """Setup para cada teste - garante logger limpo."""
        # Limpa e reconfigura o singleton
        LoggerService._instance = None
        LoggerService()

        # Cria um logger para teste
        self.logger = get_logger("test_logger")

        # Captura a saída do logger
        self.log_capture = StringIO()
        self.test_handler = logging.StreamHandler(self.log_capture)
        self.test_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        # Adiciona handler de teste ao root logger
        root = logging.getLogger()
        root.addHandler(self.test_handler)

        yield

        # Cleanup
        root.removeHandler(self.test_handler)

    def test_logger_info_method(self):
        """Verifica que o método .info() funciona."""
        self.logger.info("Test info message")
        output = self.log_capture.getvalue()
        assert "Test info message" in output

    def test_logger_error_method(self):
        """Verifica que o método .error() funciona."""
        self.logger.error("Test error message")
        output = self.log_capture.getvalue()
        assert "Test error message" in output

    def test_logger_warning_method(self):
        """Verifica que o método .warning() funciona."""
        self.logger.warning("Test warning message")
        output = self.log_capture.getvalue()
        assert "Test warning message" in output

    def test_logger_debug_method(self):
        """Verifica que o método .debug() funciona."""
        # Define nível DEBUG para o root logger
        logging.getLogger().setLevel(logging.DEBUG)

        self.logger.debug("Test debug message")
        output = self.log_capture.getvalue()
        assert "Test debug message" in output

    def test_logger_multiple_calls(self):
        """Verifica que múltiplas chamadas funcionam."""
        self.logger.info("Message 1")
        self.logger.error("Message 2")
        self.logger.warning("Message 3")

        output = self.log_capture.getvalue()
        assert "Message 1" in output
        assert "Message 2" in output
        assert "Message 3" in output


class TestLoggerIntegration:
    """Testes de integração simulando uso real."""

    def test_usage_like_timer_module(self):
        """Simula o uso do logger como no módulo timer."""
        # Limpa singleton
        LoggerService._instance = None

        # Simula import e uso no timer.py
        logger = get_logger(__name__)

        # Captura saída
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logging.getLogger().addHandler(handler)

        try:
            # Simula callback com erro
            logger.error("Erro no callback: Test exception")
            output = log_capture.getvalue()
            assert "Erro no callback: Test exception" in output
        finally:
            logging.getLogger().removeHandler(handler)

    def test_logger_in_exception_handler(self):
        """Testa logger dentro de um exception handler."""
        LoggerService._instance = None
        logger = get_logger("exception_test")

        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logging.getLogger().addHandler(handler)

        try:
            try:
                raise ValueError("Test exception")
            except Exception as e:
                logger.error(f"Erro capturado: {e}")

            output = log_capture.getvalue()
            assert "Erro capturado: Test exception" in output
        finally:
            logging.getLogger().removeHandler(handler)
