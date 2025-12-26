"""Terminal interface for FreeTimer application."""

from src.services.timer_service import TimerService
from src.services.parse_utils import parse_time
from src.interfaces.terminal.notifications import play_start_sound, play_end_sound
from rich import print


class TerminalInterface:
    """Terminal-based user interface for FreeTimer."""

    def __init__(self):
        self.service: TimerService = TimerService()

    def _create_callbacks(self, name: str) -> tuple[list, list]:
        """Create notification callbacks for a timer.

        Args:
            name: Timer identifier.

        Returns:
            Tuple of (on_start_callbacks, on_end_callbacks).
        """

        def _on_start(_timer):
            try:
                print(f"🟢 Timer '{name}' started!")
                play_start_sound()
            except Exception as e:
                print(f"Failed to notify start: {e}")

        def _on_end(_timer):
            try:
                print(f"⏰ Timer '{name}' finished!")
                play_end_sound()
            except Exception as e:
                print(f"Failed to notify end: {e}")

        return ([_on_start], [_on_end])

    def _print_timer(self, name: str, timer) -> None:
        """Display single timer details.

        Args:
            name: Timer name.
            timer: Timer instance.
        """
        duration = str(timer.duration).split(".")[0]
        remaining = str(timer.remaining).split(".")[0]

        status_color = {"running": "green", "paused": "yellow", "finished": "blue", "stopped": "red", "idle": "white"}.get(timer.status.value, "white")

        print(f" • [bold]{name}[/bold]: [{status_color}]{timer.status.value.upper()}[/{status_color}]")
        print(f"   ⏳ Duration: {duration} | Remaining: {remaining}")

    def show_menu(self) -> None:
        """Display available commands menu."""
        print("\n📋 Available Commands:")
        print("▶️  [bold red]create[/bold red]: Create timer (name, duration)")
        print("▶️  [bold red]list[/bold red]: List all timers")
        print("▶️  [bold red]start[/bold red]: Start timer (name)")
        print("▶️  [bold red]pause[/bold red]: Pause/resume timer (name)")
        print("▶️  [bold red]reset[/bold red]: Reset timer (name)")
        print("▶️  [bold red]add[/bold red]: Add time (name, duration)")
        print("▶️  [bold red]remove[/bold red]: Remove finished/stopped timer (name)")

        print("\n⚡ Special Commands:")
        print("- help: Show this menu")
        print("- exit: Exit program")

    def _cmd_criar(self) -> None:
        """Create new timer command."""
        name = input("Enter timer name: ").strip()
        print("""
⏰ Accepted time formats:
   90    = 90 seconds
   45m   = 45 minutes
   1h30m = 1 hour and 30 minutes
   30s   = 30 seconds
        """)
        duration_str = input("Enter duration: ").strip()

        try:
            duration = parse_time(duration_str)
            on_start, on_end = self._create_callbacks(name)
            timer = self.service.create_timer(name, duration, on_start=on_start, on_end=on_end)
            print(f"\n✅ Timer '{name}' created successfully!")
            self._print_timer(name, timer)
        except Exception as e:
            print(f"❌ Error creating timer: {e}")

    def _cmd_listar(self) -> None:
        """List all timers command."""
        timers = self.service.list_timers()
        if not timers:
            print("📭 No timers found.")
        else:
            print("\n📊 Timer List:")
            for name, timer in timers.items():
                self._print_timer(name, timer)

    def _cmd_iniciar(self) -> None:
        """Start timer command."""
        name = input("Enter timer name: ").strip()
        try:
            self.service.start_timer(name)
            print(f"🟢 Timer '{name}' started!")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _cmd_pausar(self) -> None:
        """Pause/resume timer command."""
        name = input("Enter timer name: ").strip()
        try:
            self.service.pause_or_resume_timer(name)
            timer = self.service.get_timer(name)
            if timer:
                status = "paused" if timer.status.value == "paused" else "resumed"
                print(f"⏸️  Timer '{name}' {status}!")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _cmd_resetar(self) -> None:
        """Reset timer command."""
        name = input("Enter timer name: ").strip()
        try:
            self.service.reset_timer(name)
            print(f"🔄 Timer '{name}' reset!")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _cmd_adicionar(self) -> None:
        """Add time to timer command."""
        name = input("Enter timer name: ").strip()
        duration_str = input("Enter time to add: ").strip()
        try:
            duration = parse_time(duration_str)
            self.service.add_time(name, duration)
            print(f"➕ Time added to timer '{name}'!")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _cmd_remover(self) -> None:
        """Remove finished/stopped timer command."""
        name = input("Enter timer name: ").strip()
        try:
            self.service.remove_timer(name)
            print(f"🗑️  Timer '{name}' removed!")
        except Exception as e:
            print(f"❌ Error: {e}")

    def run(self) -> None:
        """Run main interface loop."""
        print("🎉 Welcome to FreeTimer!")
        self.show_menu()

        while True:
            try:
                command = input("\n⌨️  Enter a command: ").lower().strip()

                if not command:
                    continue

                match command:
                    case "create":
                        self._cmd_criar()
                    case "list":
                        self._cmd_listar()
                    case "start":
                        self._cmd_iniciar()
                    case "pause":
                        self._cmd_pausar()
                    case "reset":
                        self._cmd_resetar()
                    case "add":
                        self._cmd_adicionar()
                    case "remove":
                        self._cmd_remover()
                    case "help":
                        self.show_menu()
                    case "exit":
                        break
                    case _:
                        print(f"❌ Unknown command: {command}")
                        print("💡 Use 'help' to see available commands")

            except KeyboardInterrupt:
                print("\n💡 Use 'exit' to quit the program")

        print("\n👋 Goodbye!")
