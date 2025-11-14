"""Exemplo de uso do Timer com TimerService."""

from datetime import timedelta
import time
from src.services.timer_service import TimerService


def main():
    # Cria o serviço
    service = TimerService()
    
    # Cria alguns timers
    print("📝 Criando timers...")
    service.create_timer("trabalho", timedelta(seconds=5))
    service.create_timer("pausa", timedelta(seconds=3))
    
    # Lista timers
    print("\n📋 Timers criados:")
    for name, timer in service.list_timers().items():
        print(f"  • {name}: {timer.duration} - Status: {timer.status}")
    
    # Inicia um timer
    print("\n▶️  Iniciando timer 'trabalho'...")
    service.start_timer("trabalho")
    
    # Aguarda um pouco
    time.sleep(2)
    timer = service.get_timer("trabalho")
    print(f"⏱️  Tempo restante: {timer.remaining}")
    
    # Pausa
    print("\n⏸️  Pausando...")
    service.pause_or_resume_timer("trabalho")
    time.sleep(1)
    print(f"⏱️  Ainda em: {timer.remaining} (deve estar pausado)")
    
    # Resume
    print("\n▶️  Resumindo...")
    service.pause_or_resume_timer("trabalho")
    time.sleep(2)
    print(f"⏱️  Tempo restante: {timer.remaining}")
    
    # Aguarda terminar
    print("\n⏳ Aguardando finalizar...")
    time.sleep(3)
    print(f"✅ Status final: {timer.status}")
    print(f"⏱️  Tempo restante: {timer.remaining}")


if __name__ == "__main__":
    main()
