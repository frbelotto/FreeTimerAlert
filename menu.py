from datetime import timedelta
from timer import Timer

timers = {}


# --- Funções de ação ---
def criar(nome, segundos):
    timers[nome] = Timer(duration=timedelta(seconds=segundos))
    print(f"✅ Timer '{nome}' criado com duração de {segundos} segundos.")


def iniciar(nome):
    _executar(nome, lambda t: t.start_timer())


def pausar(nome):
    _executar(nome, lambda t: t.pause_or_resume_timer())


def retomar(nome):
    _executar(nome, lambda t: t.pause_or_resume_timer())


def resetar(nome):
    _executar(nome, lambda t: t.reset_timer())


def adicionar(nome, segundos):
    _executar(nome, lambda t: t.add_time(timedelta(seconds=segundos)))


def listar():
    print("📦 Timers ativos:")
    for nome, timer in timers.items():
        estado = "▶️ rodando" if timer.running else "⏸️ pausado"
        restante = timer.remaining if timer.remaining else timer.duration
        print(f" - {nome}: {estado}, restante: {str(restante).split('.')[0]}")


# --- Dicionário de comandos ---
comandos = {
    1: ("criar", criar),
    2: ("iniciar", iniciar),
    3: ("pausar", pausar),
    4: ("retomar", retomar),
    5: ("resetar", resetar),
    6: ("adicionar", adicionar),
    7: ("listar", listar),
    8: ("sair", None),
}


# --- Funções auxiliares ---
def exibir_menu():
    print("\n📋 Comandos disponíveis:")
    for codigo, (nome, _) in comandos.items():
        if nome in ["criar", "adicionar"]:
            print(f"{codigo}. {nome} <nome> <segundos>")
        elif nome == "listar":
            print(f"{codigo}. {nome}")
        elif nome != "sair":
            print(f"{codigo}. {nome} <nome>")
        else:
            print(f"{codigo}. {nome}")


def executar_comando(ncomando, comando):
    if not comando:
        return

    # Determina qual comando usar
    if ncomando in comandos:
        nome, funcao = comandos[ncomando]
    else:
        chave = comando[0].lower()
        for _, (n, f) in comandos.items():
            if chave == n:
                nome, funcao = n, f
                break
        else:
            print("❌ Comando inválido.")
            return

    args = comando[1:]

    try:
        if nome == "criar" and len(args) == 2:
            criar(args[0], int(args[1]))
        elif nome == "iniciar" and len(args) == 1:
            iniciar(args[0])
        elif nome == "pausar" and len(args) == 1:
            pausar(args[0])
        elif nome == "retomar" and len(args) == 1:
            retomar(args[0])
        elif nome == "resetar" and len(args) == 1:
            resetar(args[0])
        elif nome == "adicionar" and len(args) == 2:
            adicionar(args[0], int(args[1]))
        elif nome == "listar":
            listar()
        elif nome == "sair":
            print("👋 Encerrando...")
            exit()
        else:
            print("❌ Argumentos inválidos.")
    except Exception as e:
        print(f"⚠️ Erro: {e}")


def _executar(nome, acao):
    if nome in timers:
        acao(timers[nome])
    else:
        print("❌ Timer não encontrado.")
