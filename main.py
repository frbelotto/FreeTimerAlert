from terminal import main_terminal
#A ser importado e configurada a versão do PySide6

if __name__ == "__main__":
    comandos_possíveis = {1: "Terminal", 2: "Gui - PySide6"}
    execuções_possíveis = {1: main_terminal, 2: "main_gui"}

    comando = input(f"Digite a versão a ser executada: {comandos_possíveis} : ")
    try:
        comando = int(comando)
        if comando not in comandos_possíveis.keys():
            print(f"O comando informado {comando} é inválido, seu burro!")
        else:
            execuções_possíveis[comando]()
    except ValueError:
        print(f"O comando informado {comando} é inválido, seu burro!")
