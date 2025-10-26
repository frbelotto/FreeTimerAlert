import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
    QHBoxLayout,
)
from src.services.menu import executar_comando


class TimerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Timers (Visual)")
        self.resize(600, 400)

        # Widgets principais
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Entrada de comando (igual terminal)
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Digite comando (ex: criar t1 10)")
        self.run_btn = QPushButton("Executar comando")

        # Saída de logs
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # Layout de entrada
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.run_btn)

        layout.addLayout(input_layout)
        layout.addWidget(QLabel("Saída:"))
        layout.addWidget(self.output)

        # Conexões
        self.run_btn.clicked.connect(self.run_command)
        self.input_line.returnPressed.connect(self.run_command)

    def run_command(self):
        comando = self.input_line.text().strip().split()
        if not comando:
            return
        # Redireciona prints para a saída visual
        from io import StringIO
        import sys

        buffer = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        try:
            executar_comando(comando)
        finally:
            sys.stdout = sys_stdout
        # Mostra resultado no QTextEdit
        saida = buffer.getvalue()
        if saida:
            self.output.append(saida.strip())
        self.input_line.clear()


def main():
    app = QApplication(sys.argv)
    gui = TimerGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
