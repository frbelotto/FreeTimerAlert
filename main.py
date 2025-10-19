from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional


class Clock (BaseModel):
    """ Classe básica para o controle da duração e execução do timer"""
    
    start: datetime = Field(default_factory=datetime.now,  frozen=True)
    duration : str
    duration_parse: Optional[timedelta] = None
    end: Optional[datetime] = None
    
    def model_post_init(self, __context):
        self.start_timer()

    def start_timer (self):
        minutos, segundos = map(int, self.duration.split(":"))
        self.duration_parse = timedelta(minutes=minutos, seconds=segundos)
        self.end = self.start + self.duration_parse
        self.relógio()

    def pause_timer(self):
        pass

    def encerrar_timer(self):
        pass

    def relógio(self):
        print(self.end)
            # while datetime.now() < self.end:

                # print (datetime.now())

if __name__ == "__main__":
    entrada = input("Digite o tempo em minutos e segundos (formato mm:ss): ")
    a = Clock(duration=entrada)


# import asyncio

# async def main():
#     entrada = input("Digite o tempo em minutos e segundos (formato mm:ss): ")
#     a = Clock(duration=entrada)
#     a.start_timer()
#     await a.relógio()

# asyncio.run(main())
