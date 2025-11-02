from datetime import timedelta
from pydantic import BaseModel
from typing import Callable
from src.interfaces.base_interface import TimerInterface
from src.services.parse_utils import parse_time
import inspect
from rich import print




class CommandInfo (BaseModel):
    """Informações sobre um comando específico"""
    name: str           # Nome do comando (ex: criar)
    description: str    # Descrição do comando
    handler: Callable   # Função que executa o comando

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
            description = parts[1] if len(parts) > 1 else ""
            
            command_info[cmd_name] = CommandInfo(
                name=cmd_name,
                description=description,
                handler=handler
            )
            
        return command_info

    def show_menu(self) -> None:
        """Mostra o menu com os comandos disponíveis."""
        print('\n📋 Comandos Disponíveis: Comandos que exigem parâmetros, estes devem ser nomeados (kwargs)')
        for i, (name, info) in enumerate(self.commands.items(), 1):
            print(f"▶️  [bold red]{name}[/bold red]: {info.description}")
        
        print("\n⚡ Comandos Especiais:")
        print("- ajuda: Mostra este menu")
        print("- sair: Encerra o programa")
        

    def run(self) -> None:
        """Executa o loop principal da interface."""
        print("🎉 Bem-vindo ao FreeTimer!")
        self.show_menu()
        
        while True:
            try:
                # Captura e processa o comando
                command = input("\n⌨️  Digite um comando: ").lower().strip().split()
                if not command:
                    continue

                cmd = command[0]

                # Comandos especiais
                if cmd == 'sair':
                    break

                # Processa comandos registrados
                if cmd not in self.commands:
                    print(f"❌ Comando desconhecido: {cmd}")
                    print("💡 Use 'ajuda' para ver os comandos disponíveis")
                    continue
                
                # print(f'Executando : Comando {self.commands[cmd]} , argumentos {args}')
                try:
                    handler = self.commands[cmd].handler

                    
                    sig = inspect.signature(handler)
                    kwargs = {}
                    for param in sig.parameters.values():
                        # print(param.name, param.default, param.annotation)
                        
                        if param.annotation is timedelta:
                            print('''
                                ⏰ Formatos de tempo aceitos:
                                90    = 90 segundos
                                45m   = 45 minutos
                                1h30m = 1 hora e 30 minutos
                                30s   = 30 segundos
                                ''')
                        value = input(f"Digite o valor para o parâmetro '{param.name}', que é do tipo ({param.annotation}): ")

                        if param.annotation is timedelta:
                            value = parse_time(value)

                        if value:
                            kwargs[param.name] = value

                    result = handler(**kwargs)
                    if result is not None:
                        print(result)

                except Exception as e:
                    print(f'Deu ruim {e}')
                

            except KeyboardInterrupt:
                print("\n💡 Use 'sair' para encerrar o programa")

        print("\n👋 Até mais!")