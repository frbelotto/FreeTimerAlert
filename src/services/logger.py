from __future__ import annotations

import logging


class LoggerService:
    """Singleton para gerenciar logging do sistema.
    """
    
    _instance: LoggerService | None = None
    
    def __new__(cls) -> LoggerService:
        """Garante que apenas uma instância exista (padrão Singleton).
        
        Sempre que você faz LoggerService(), retorna a MESMA instância.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_root_logger()
        return cls._instance
    
    def _setup_root_logger(self) -> None:
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.handlers.clear()
        
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    service = LoggerService()  # Sempre retorna a MESMA instância
    return service.get_logger(name)
