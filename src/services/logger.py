import logging


def setup_logging(log_level: int = logging.INFO, log_file: str = "freetimer.log") -> None:
    """
    Configura o sistema de logging com dois handlers:
    - Console: Mostra apenas a mensagem de forma limpa
    - Arquivo: Registra logs detalhados com timestamp e nível

    Args:
        log_level: Nível de logging (default: logging.INFO)
        log_file: Nome do arquivo de log (default: freetimer.log)
    """
    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove handlers existentes para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 1. Handler para Console (formato simples)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter("%(message)s")  # Apenas a mensagem
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 2. Handler para Arquivo (formato detalhado)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado para o módulo especificado.

    Args:
        name: Nome do módulo/componente para o logger

    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)
