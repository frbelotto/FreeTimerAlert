from dataclasses import dataclass
from typing import Any, Callable
from src.interfaces.base_interface import TimerInterface
from src.services.parse_utils import parse_time


@dataclass
class CommandInfo:
    """Informações sobre um comando específico"""
    name: str           # Nome do comando (ex: criar)
    description: str    # Descrição do comando
    handler: Callable   # Função que executa o comando
    min_args: int      # Número mínimo de argumentos
    max_args: int      # Número máximo de argumentos
    usage: str         # Como usar o comando


class TerminalInterface(TimerInterface):
    """Interface de terminal simplificada para o FreeTimer."""
  
    def __init__(self):
        super().__init__()
        # Mapeia os serviços disponíveis para informações de comando
        self.commands = self._setup_commands()

    def _setup_commands(self) -> dict[str, CommandInfo]:
        """Configura os comandos disponíveis a partir dos serviços"""
        available = self.service.available_services
        command_info = {}
        
        # Parse dos serviços disponíveis
        for service_info, handler in available.items():
            # Exemplo do formato: "1: Criar : Criar timers (nome, duração)"
            parts = service_info.split(' : ')
                
            # Extrai as informações do serviço
            cmd_name = parts[0].lower()  # Pega o nome do comando (ex: "Criar" -> "criar")
            description = parts[1] if len(parts) > 2 else ""
            
            # Determina os parâmetros do comando baseado na descrição
            if "(nome, duração)" in description:
                min_args = max_args = 2
                usage = f"{cmd_name} <nome> <tempo>"
                handler_func = self._handle_create if cmd_name == "criar" else self._handle_add_time
            elif "(nome)" in description:
                min_args = max_args = 1
                usage = f"{cmd_name} <nome>"
                # Cria uma função específica para este comando
                def handler_for_command(name: str, cmd=cmd_name) -> None:
                    return self._handle_simple_command(cmd, name)
                handler_func = handler_for_command
            else:
                min_args = max_args = 0
                usage = cmd_name
                handler_func = self._handle_list
            
            # Registra o comando
            command_info[cmd_name] = CommandInfo(
                name=cmd_name,
                description=description,
                handler=handler_func,
                min_args=min_args,
                max_args=max_args,
                usage=usage
            )
            
        return command_info

    def show_menu(self) -> None:
        """Mostra o menu com os comandos disponíveis."""
        print('\n📋 Comandos Disponíveis:')
        for i, (name, info) in enumerate(self.commands.items(), 1):
            print(f"{i}. {name}: {info.description}")
            print(f"   Uso: {info.usage}")
        
        print("\n⚡ Comandos Especiais:")
        print("- ajuda: Mostra este menu")
        print("- sair: Encerra o programa")
        
        print('''
            ⏰ Formatos de tempo aceitos:
            90    = 90 segundos
            45m   = 45 minutos
            1h30m = 1 hora e 30 minutos
            30s   = 30 segundos
            ''')

    def _handle_create(self, name: str, time: str) -> None:
        """Trata o comando de criar timer"""
        duration = parse_time(time)
        self.service.create_timer(name, duration)
        print(f"✅ Timer '{name}' criado com duração de {duration}")

    def _handle_list(self) -> None:
        """Trata o comando de listar timers"""
        timers = self.service.list_timers()
        if not timers:
            print("ℹ️ Nenhum timer criado")
            return
            
        print("\n📋 Timers Ativos:")
        for name, timer in timers.items():
            state = "▶️" if timer.running else "⏸️"
            remaining = timer.remaining if timer.remaining else timer.duration
            print(f"{state} {name}: {remaining}")

    def _handle_simple_command(self, cmd: str, name: str) -> None:
        """Trata comandos simples que recebem apenas o nome do timer"""
        method = getattr(self.service, f"{cmd}_timer")
        method(name)
        timer = self.service.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não encontrado")
        state = "▶️" if timer.running else "⏸️"
        remaining = timer.remaining if timer.remaining else timer.duration
        print(f"{state} {name}: {remaining}")

    def _handle_add_time(self, name: str, time: str) -> None:
        """Trata o comando de adicionar tempo"""
        duration = parse_time(time)
        self.service.add_time(name, duration)
        timer = self.service.get_timer(name)
        if not timer:
            raise ValueError(f"Timer '{name}' não encontrado")
        state = "▶️" if timer.running else "⏸️"
        remaining = timer.remaining if timer.remaining else timer.duration
        print(f"⏱️ Adicionado {duration} ao timer {name}")
        print(f"{state} Tempo atual: {remaining}")

    def run(self) -> None:
        """Executa o loop principal da interface."""
        print("🎉 Bem-vindo ao FreeTimer!")
        self.show_menu()
        
        while True:
            try:
                # Captura e processa o comando
                command = input("\n⌨️ Digite um comando: ").strip().split()
                if not command:
                    continue

                cmd, *args = command
                cmd = cmd.lower()

                # Comandos especiais
                if cmd == 'sair':
                    break
                if cmd == 'ajuda':
                    self.show_menu()
                    continue

                # Processa comandos registrados
                if cmd not in self.commands:
                    print(f"❌ Comando desconhecido: {cmd}")
                    print("💡 Use 'ajuda' para ver os comandos disponíveis")
                    continue

                # Valida número de argumentos
                command_info = self.commands[cmd]
                if not (command_info.min_args <= len(args) <= command_info.max_args):
                    print(f"❌ Uso incorreto. Use: {command_info.usage}")
                    continue

                # Executa o comando
                try:
                    command_info.handler(*args)
                except (ValueError, RuntimeError) as e:
                    print(f"❌ Erro: {str(e)}")
                except Exception as e:
                    print(f"❌ Erro inesperado: {str(e)}")

            except KeyboardInterrupt:
                print("\n💡 Use 'sair' para encerrar o programa")

        print("\n👋 Até mais!")