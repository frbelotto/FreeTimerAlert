import threading
from datetime import timedelta
from time import sleep
from typing import Callable

from pydantic import BaseModel, validate_call, Field


class Timer(BaseModel):
    """Classe básica para o controle da duração e execução do timer"""

    duration: timedelta
    remaining: timedelta | None = None
    running: bool = False
    stop_signal: bool = False

    # Use default_factory to avoid shared mutable defaults between instances
    on_start: list[Callable] = Field(default_factory=list)
    on_end: list[Callable] = Field(default_factory=list)

    def start_timer(self):
        if self.running:
            print("⚠️ Timer já está em execução.")
            return
        self.running = True
        self.stop_signal: bool = False  # 🔴 Novo atributo para sinalizar parada
        # print("🟢 Timer iniciado")
        self.notify("start")  # 🔔 dispara evento de início
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        if self.remaining is None:
            self.remaining = self.duration

        while self.remaining > timedelta(seconds=0) and not self.stop_signal:
            if self.running:
                print(f"Tempo restante: {self.remaining}")  # , at {datetime.datetime.now()}")
                sleep(1)
                self.remaining -= timedelta(seconds=1)
            else:
                sleep(0.1)  # ⬅️ Espera leve enquanto pausado
        if not self.stop_signal:
            self.notify("end")  # 🔔 dispara evento de fim
            # print("⏰ Timer finalizado!")
        else:
            print("🔴 Timer resetado!")
        self.running = False
        self.remaining = self.duration

    def pause_or_resume_timer(self):
        self.running = not self.running
        print("▶️ Timer retomado." if self.running else "⏸️ Timer pausado.")

    @validate_call()
    def add_time(self, extra: timedelta):
        if self.remaining:
            self.remaining += extra
            print(f"⏱️ Tempo adicionado: {extra}. Novo tempo restante: {self.remaining}")

    def reset_timer(self):
        if self.running or self.remaining:
            self.stop_signal = True  # ⛔ Sinaliza para encerrar a thread
            self.running = False
            self.remaining = self.duration
            print("🔁 Timer será resetado...")

    @validate_call()
    def notify(self, event: str):
        callbacks = {
            "start": self.on_start,
            "end": self.on_end,
        }
        for callback in callbacks.get(event, []):
            try:
                callback(self)
            except Exception as e:
                print(f"Erro na notificação '{event}': {e}")


if __name__ == "__main__":
    timer = Timer(duration=timedelta(seconds=10))
    timer.start_timer()
    sleep(4)
    timer.pause_or_resume_timer()
    sleep(5)
    timer.pause_or_resume_timer()
    timer.add_time(timedelta(seconds=5))
    sleep(3)
    timer.reset_timer()
