import datetime
import threading
from datetime import timedelta
from time import sleep

from pydantic import BaseModel, validate_call


class Timer(BaseModel):
    """Classe básica para o controle da duração e execução do timer"""

    duration: timedelta
    remaining: timedelta | None = None
    running: bool = False


    def start_timer(self):
        if self.running:
            print("⚠️ Timer já está em execução.")
            return
        self.running = True
        print("🟢 Timer iniciado")
        threading.Thread(target=self.run, daemon=False).start()  

    def run(self):
        if self.remaining is None:
            self.remaining = self.duration
        while self.remaining > timedelta(seconds=0):
            if self.running:
                print(f"Tempo restante: {self.remaining}, at {datetime.datetime.now()}")
                sleep(1)
                self.remaining -= timedelta(seconds=1)
            else:
                sleep(0.1)  # ⬅️ Espera leve enquanto pausado
        print("⏰ Timer finalizado!")
        self.running = False

    def pause_or_resume_timer(self):
        self.running = not self.running
        print("▶️ Timer retomado." if self.running else "⏸️ Timer pausado.")

    @validate_call()
    def add_time(self, extra: timedelta):
        if self.remaining:
            self.remaining += extra
            print(f"⏱️ Tempo adicionado: {extra}. Novo tempo restante: {self.remaining}")



timer = Timer(duration=timedelta(seconds=10))
timer.start_timer()
sleep(4)
timer.pause_or_resume_timer()
sleep(5)
timer.pause_or_resume_timer()
timer.add_time(timedelta(seconds=5))

