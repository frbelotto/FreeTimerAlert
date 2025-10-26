from datetime import timedelta
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QListWidget,
    QMessageBox,
    QHBoxLayout,
    QSpinBox,
)
from PySide6.QtCore import Qt, QTimer
from src.interfaces.base_interface import TimerInterface


class GuiInterface(TimerInterface, QMainWindow):
    def __init__(self):
        TimerInterface.__init__(self)
        QMainWindow.__init__(self)

        self.setWindowTitle("FreeTimer")
        self.setup_ui()

        # Timer para atualizar a lista de timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_timer_list)
        self.update_timer.start(1000)  # Atualiza a cada segundo

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Criar timer
        create_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do Timer")
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 86400)  # 1 segundo até 24 horas
        self.duration_input.setValue(60)
        self.create_button = QPushButton("Criar Timer")
        self.create_button.clicked.connect(self.create_timer)

        create_layout.addWidget(self.name_input)
        create_layout.addWidget(self.duration_input)
        create_layout.addWidget(self.create_button)
        layout.addLayout(create_layout)

        # Lista de timers
        self.timer_list = QListWidget()
        layout.addWidget(self.timer_list)

        # Botões de controle
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar")
        self.pause_button = QPushButton("Pausar")
        self.reset_button = QPushButton("Resetar")
        self.add_time_input = QSpinBox()
        self.add_time_input.setRange(1, 3600)
        self.add_time_input.setValue(60)
        self.add_time_button = QPushButton("Adicionar Tempo")

        self.start_button.clicked.connect(self.start_selected_timer)
        self.pause_button.clicked.connect(self.pause_selected_timer)
        self.reset_button.clicked.connect(self.reset_selected_timer)
        self.add_time_button.clicked.connect(self.add_time_to_selected)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addWidget(self.add_time_input)
        control_layout.addWidget(self.add_time_button)
        layout.addLayout(control_layout)

    def create_timer(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Erro", "Por favor, insira um nome para o timer")
            return

        try:
            duration = timedelta(seconds=self.duration_input.value())
            self.service.create_timer(name, duration)
            self.name_input.clear()
            self.update_timer_list()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

    def update_timer_list(self):
        self.timer_list.clear()
        for name, timer in self.service.list_timers().items():
            state = "▶️ rodando" if timer.running else "⏸️ pausado"
            remaining = timer.remaining if timer.remaining else timer.duration
            self.timer_list.addItem(f"{name}: {state}, restante: {str(remaining).split('.')[0]}")

    def get_selected_timer_name(self):
        current = self.timer_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um timer")
            return None
        return current.text().split(":")[0]

    def start_selected_timer(self):
        if name := self.get_selected_timer_name():
            try:
                self.service.start_timer(name)
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def pause_selected_timer(self):
        if name := self.get_selected_timer_name():
            try:
                self.service.pause_timer(name)
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def reset_selected_timer(self):
        if name := self.get_selected_timer_name():
            try:
                self.service.reset_timer(name)
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def add_time_to_selected(self):
        if name := self.get_selected_timer_name():
            try:
                self.service.add_time(name, timedelta(seconds=self.add_time_input.value()))
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def run(self) -> None:
        """Inicia a interface gráfica"""
        app = QApplication([])
        self.show()
        app.exec()

    def show_menu(self) -> None:
        """Não aplicável para interface gráfica"""
        pass
