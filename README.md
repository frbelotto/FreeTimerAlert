FreeTimer é um timer simples e extensível. Hoje ele oferece uma interface de Terminal funcional; outras interfaces (GUI e Web) serão adicionadas futuramente. O core é desacoplado e pensado para ser fácil de evoluir.

## Como usar (Interface de Terminal)

Pré‑requisitos:
- Python 3.13+
- uv (opcional, mas recomendado)

Passos:
1) Instalar dependências
	 - `uv sync`
2) Executar o programa
	 - `uv run python main.py`
3) Escolher a interface “Terminal” e usar os comandos:
	 - `criar` (name: str, duration: tempo)
	 - `listar`
	 - `iniciar` (name: str)
	 - `pausar` (name: str)  → alterna entre pausar/retomar
	 - `resetar` (name: str)
	 - `adicionar` (name: str, duration: tempo)

Formato de tempo aceito (duration):
- `90`  → 90 segundos
- `45m` → 45 minutos
- `1h30m` → 1 hora e 30 minutos
- `30s` → 30 segundos

Exemplo de sessão:
```
🎉 Bem-vindo ao FreeTimer!
▶️  criar: Criar timers (name, duration)
▶️  iniciar: Iniciar timer (name)
...

⌨️  Digite um comando: criar
Digite o valor para 'name' (texto): foco
⏰ Formatos de tempo aceitos...
Digite o valor para 'duration' (tempo (90, 45m, 1h30m, 30s)): 25m

⌨️  Digite um comando: iniciar
Digite o valor para 'name' (texto): foco
🟢 Timer 'foco' foi iniciado!
Tempo restante: 0:24:59
...
```

Áudio de notificação:
- Início: `Assets/Sounds/clock-start.mp3`
- Fim: `Assets/Sounds/timer-terminer.mp3`
- Desabilitar áudio (CI/servidor/sem backend): `FREETIMER_MUTE=1`

Observação: se seu sistema não tiver backend de áudio disponível (ALSA/PulseAudio etc.), o programa continuará funcionando e registrará um aviso ao tentar tocar sons.

## Como funciona (por dentro)

### Arquitetura

O FreeTimer segue uma arquitetura em camadas com separação clara de responsabilidades:

**Timer** (`src/core/timer.py`)
- Responsabilidade: Modelo de dados + lógica de contagem
- Gerencia: duração, tempo restante, status
- Métodos: `start()`, `pause()`, `resume()`, `stop()`, `reset()`, `tick()`
- **Sem threading** (mantém simplicidade e testabilidade)

**TimerService** (`src/services/timer_service.py`)
- Responsabilidade: Orquestrador de execução
- Gerencia: múltiplos timers + threads de execução
- Métodos: `create_timer()`, `start_timer()`, `stop_timer()`, `pause_or_resume_timer()`
- Coordena: uma thread por timer ativo

**Interface** (terminal, GUI, web)
- Responsabilidade: Interação com usuário
- Traduz comandos do usuário para chamadas do TimerService
- Anexa callbacks de notificação aos timers

**Notificações** (`notifications.py` + implementações)
- Contrato abstrato e implementações que tocam sons ou mostram alertas

### Fluxo de Execução

```
1. service.create_timer("trabalho", timedelta(minutes=25))
   └─> Cria Timer + threading.Event

2. service.start_timer("trabalho")
   └─> timer.start() (marca como RUNNING)
   └─> Cria thread background para executar ticks
   └─> Dispara callback on_start

3. Loop em background (thread dedicada):
   └─> Enquanto não receber sinal de parada:
       └─> Se timer.status == RUNNING:
           └─> timer.tick(seconds=1)
       └─> Aguarda 1 segundo

4. Quando timer.remaining chega a zero:
   └─> timer.status = FINISHED
   └─> Dispara callback on_end
```

Componentes principais:
- Core (`src/core/timer.py`): modelo simples que gerencia estado e lógica de contagem. Expõe eventos `on_start` e `on_end` (padrão Observer).
- Serviço (`src/services/timer_service.py`): gerencia vários timers por nome, cria threads para execução em background, expõe operações de alto nível.
- Interface de Terminal (`src/interfaces/terminal/terminal.py`): roteia comandos do usuário para o serviço e anexa callbacks de notificação.
- Notificações (`src/interfaces/notifications.py` + `src/interfaces/terminal/terminal_notification.py`): contrato abstrato e implementação que toca sons no Terminal.

### Diagrama de arquitetura

#### Visão geral do sistema

```mermaid
flowchart TB
    subgraph UI["🖥️ Camada de Interface"]
        Terminal[Terminal Interface]
        GUI[GUI Interface<br/><i>futuro</i>]
        Web[Web Interface<br/><i>futuro</i>]
    end
    
    subgraph Service["⚙️ Camada de Serviço"]
        TS[TimerService<br/>- Gerencia timers<br/>- Cria threads<br/>- Coordena execução]
    end
    
    subgraph Core["💾 Camada de Domínio"]
        T1[Timer: trabalho<br/>25min]
        T2[Timer: pausa<br/>5min]
        T3[Timer: almoço<br/>1h]
    end
    
    subgraph Threads["🧵 Threads de Execução"]
        TH1[Thread 1<br/>tick a cada 1s]
        TH2[Thread 2<br/>tick a cada 1s]
    end
    
    subgraph Notify["🔔 Notificações"]
        NS[NotificationService<br/>- Toca sons<br/>- Mostra alertas]
    end
    
    Terminal --> TS
    GUI -.-> TS
    Web -.-> TS
    
    TS -->|cria/gerencia| T1
    TS -->|cria/gerencia| T2
    TS -->|cria/gerencia| T3
    
    TS -->|inicia| TH1
    TS -->|inicia| TH2
    
    TH1 -.->|timer.tick()| T1
    TH2 -.->|timer.tick()| T2
    
    T1 -->|on_start/on_end| NS
    T2 -->|on_start/on_end| NS
    T3 -->|on_start/on_end| NS
```

#### Gerenciamento de múltiplos timers

```mermaid
graph TB
    subgraph TS["TimerService"]
        direction TB
        TM["_timers = {<br/>'trabalho': Timer1,<br/>'pausa': Timer2<br/>}"]
        TH["_threads = {<br/>'trabalho': Thread1,<br/>'pausa': Thread2<br/>}"]
        EV["_stop_events = {<br/>'trabalho': Event1,<br/>'pausa': Event2<br/>}"]
    end
    
    subgraph Thread1["Thread 1: trabalho"]
        L1["Loop infinito:<br/>while not Event1.is_set():<br/>  Timer1.tick()<br/>  sleep(1s)"]
    end
    
    subgraph Thread2["Thread 2: pausa"]
        L2["Loop infinito:<br/>while not Event2.is_set():<br/>  Timer2.tick()<br/>  sleep(1s)"]
    end
    
    TH --> Thread1
    TH --> Thread2
    
    Thread1 -.->|decrementa| TM
    Thread2 -.->|decrementa| TM
    
    EV -.->|controla| Thread1
    EV -.->|controla| Thread2
    
    style Thread1 fill:#e1f5e1
    style Thread2 fill:#e1f5e1
```

### Sequência de execução

#### Criando e iniciando múltiplos timers

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant UI as Terminal
    participant S as TimerService
    participant T1 as Timer: trabalho
    participant T2 as Timer: pausa
    participant TH1 as 🧵 Thread 1
    participant TH2 as 🧵 Thread 2
    participant N as 🔔 Notificações

    U->>UI: criar trabalho 25m
    UI->>S: create_timer("trabalho", 25m)
    S->>T1: new Timer(25m)
    S->>S: _stop_events["trabalho"] = Event()
    
    U->>UI: criar pausa 5m
    UI->>S: create_timer("pausa", 5m)
    S->>T2: new Timer(5m)
    S->>S: _stop_events["pausa"] = Event()
    
    U->>UI: iniciar trabalho
    UI->>S: start_timer("trabalho")
    S->>T1: start()
    T1->>N: on_start callback
    N->>N: 🔊 toca som início
    S->>TH1: Thread(target=_run_timer, args=("trabalho",))
    activate TH1
    TH1->>TH1: while not stopped
    
    U->>UI: iniciar pausa
    UI->>S: start_timer("pausa")
    S->>T2: start()
    T2->>N: on_start callback
    N->>N: 🔊 toca som início
    S->>TH2: Thread(target=_run_timer, args=("pausa",))
    activate TH2
    TH2->>TH2: while not stopped
    
    loop A cada 1 segundo
        TH1->>T1: tick()
        T1->>T1: remaining -= 1s
        TH2->>T2: tick()
        T2->>T2: remaining -= 1s
    end
    
    Note over TH2,T2: Pausa termina primeiro (5min)
    T2->>T2: status = FINISHED
    T2->>N: on_end callback
    N->>N: 🔊 toca som fim
    deactivate TH2
    
    Note over TH1,T1: Trabalho continua (25min)
    T1->>T1: status = FINISHED
    T1->>N: on_end callback
    N->>N: 🔊 toca som fim
    deactivate TH1
```

#### Pausando e retomando um timer

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant UI as Terminal
    participant S as TimerService
    participant T as Timer: trabalho
    participant TH as 🧵 Thread

    Note over T: Status: RUNNING<br/>Remaining: 15:00

    U->>UI: pausar trabalho
    UI->>S: pause_or_resume_timer("trabalho")
    S->>T: pause()
    T->>T: status = PAUSED
    
    Note over TH: Thread continua rodando,<br/>mas tick() retorna sem fazer nada
    
    loop Thread ativa
        TH->>T: tick()
        T->>T: status != RUNNING, retorna
        Note over T: Remaining: 15:00<br/>(não decrementa)
    end
    
    U->>UI: pausar trabalho (toggle)
    UI->>S: pause_or_resume_timer("trabalho")
    S->>T: resume()
    T->>T: status = RUNNING
    
    Note over TH: Thread volta a decrementar
    
    loop A cada 1s
        TH->>T: tick()
        T->>T: remaining -= 1s
    end
```

## Desenvolvimento

Rodar, formatar e validar:
- Executar: `uv run task run` ou `uv run python main.py`
- Formatação: `uvx ruff format`
- Lint: `uvx ruff check`

Testes (pytest):
- `uv run pytest tests/ -v`
- Dica: os testes executam com `FREETIMER_MUTE=1` para não tocar áudio.

Estrutura do projeto (resumo):
```
main.py
src/
	core/timer.py
	services/timer_service.py
	interfaces/
		base_interface.py
		terminal/
			terminal.py
			terminal_notification.py
		notifications.py
Assets/Sounds/*.mp3
tests/
	conftest.py
	test_timer.py
```

## Empacotando em executável (opcional)

Com PyInstaller (Linux):
```
uvx pyinstaller --onefile --name freetimer --console main.py \
	--add-data "Assets/Sounds:Assets/Sounds"
```
Depois, execute `./dist/freetimer`.

Observação: para ambientes gráficos e Web, novas interfaces serão adicionadas no futuro. A atual documentação foca na interface de Terminal.