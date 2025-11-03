from playsound3 import playsound
from time import sleep
from src.interfaces.notifications import NotificationService

class TerminalNotificationService(NotificationService):
    def on_timer_start(self, name: str):
        print(f"🟢 Timer '{name}' foi iniciado!")
        playsound("Assets/Sounds/clock-start.mp3", block=False)

    def on_timer_end(self, name: str):
        print(f"⏰ Timer '{name}' foi concluído!")
        sound = playsound("Assets/Sounds/timer-terminer.mp3", block=False)
        sleep(5)
        try:
            sound.stop()
        except Exception:
            pass

