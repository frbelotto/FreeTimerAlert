from menu import exibir_menu, executar_comando


def main_terminal():
    print("⏱️ Gerenciador de Timers")
    while True:
        exibir_menu()

        entrada = input("Digite o comando: ").lower().strip().split()

        if not entrada:
            continue

        try:
            ncomando = int(entrada[0])
        except ValueError:
            ncomando = None

        if (ncomando == 0) or (entrada[0] == "sair"):
            print("👋 Encerrando...")
            break
        executar_comando(ncomando, entrada)
