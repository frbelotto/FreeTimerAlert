from enum import Enum
from typing import Dict, Type
from src.services.logger import get_logger, setup_logging
from src.interfaces.base_interface import TimerInterface
import importlib

# Configura o logger global para o módulo
logger = get_logger(__name__)


class Interfaces(Enum):
    """Define as interfaces disponíveis no sistema.

    Cada membro do enum armazena uma tupla (caminho_do_modulo, nome_da_classe).
    Use get_class() para obter a classe da interface e create() para instanciar.
    """

    TERMINAL = ("src.interfaces.terminal.terminal", "TerminalInterface")
    # WEB = ("src.interfaces.web.gui", "WebInterface")
    # GUI = ("src.interfaces.gui.gui", "GuiInterface")

    def get_class(self) -> Type[TimerInterface]:
        """Retorna a classe da interface (sem instanciar)"""

        module_path, class_name = self.value
        try:
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except ImportError as e:
            raise NotImplementedError(f"Interface {self.name} não disponível: {e}")
        except AttributeError:
            raise NotImplementedError(f"Classe {class_name} não encontrada em {module_path}")


class InterfaceManager:
    """Gerencia as interfaces disponíveis e suas execuções (lazy loading)"""

    def __init__(self):
        self._interfaces: Dict[Interfaces, TimerInterface] = {}  # Cache de instâncias já criadas

    def show_interface_menu(self) -> None:
        """Exibe o menu de seleção de interface"""
        logger.info("\n🕒 FreeTimer - Selecione a Interface:")
        for i, interface in enumerate(Interfaces, 1):
            logger.info(f"{i}. {interface.name.title()}")
        logger.info("q. Sair")

    def get_interface(self, interface_type: Interfaces) -> TimerInterface:
        """Retorna uma interface, criando-a se necessário (lazy loading)"""
        if interface_type not in self._interfaces:
            interface_class = interface_type.get_class()
            self._interfaces[interface_type] = interface_class()
        return self._interfaces[interface_type]


def run_interface() -> None:
    """Executa a interface selecionada pelo usuário"""
    manager = InterfaceManager()

    while True:
        manager.show_interface_menu()
        choice = input("\nEscolha uma opção: ").lower().strip()

        if choice == "q":
            logger.info("👋 Encerrando o programa...")
            break

        try:
            interface_num = int(choice)
            interface = list(Interfaces)[interface_num - 1]
            logger.info(f"Iniciando interface {interface.name}")

            # Obtém e executa a interface (cria apenas quando necessário)
            interface_obj = manager.get_interface(interface)
            interface_obj.run()

        except ValueError:
            logger.error("⚠️ Entrada inválida, por favor, digite um número válido ou 'q' para sair.")
        except IndexError:
            logger.error("⚠️ Opção inválida. Escolha uma das opções disponíveis.")
        except NotImplementedError as e:
            logger.warning(str(e))
            logger.warning("⚠️ Esta interface ainda não está disponível.")
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            logger.error("❌ Ocorreu um erro inesperado.")


if __name__ == "__main__":
    # Configura o logger antes de qualquer uso
    setup_logging()
    logger.info("Iniciando FreeTimer")
    run_interface()
