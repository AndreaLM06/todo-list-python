from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QWidget, QLabel, QListView, QVBoxLayout

from task_model import TaskModel


class TodayTaskPage(QWidget):
    """
    Classe pour la page du jour qui liste les tâches du jour
    """
    page_loaded = Signal()

    def __init__(self, conn):
        super().__init__()
        self.today_tasks_label = None
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.today_tasks_model = TaskModel()
        self.today_tasks_list = QListView()
        self.init_ui()

    def init_ui(self):
        """
        Méthode pour initialiser l'interface utilisateur de la page du jour

        Args:
            None
        Returns:
            None
        """
        # Layout principal
        lists_layout = QVBoxLayout()

        # To Do List
        self.today_tasks_label = QLabel("The tasks of the day")
        self.today_tasks_label.setAlignment(Qt.AlignHCenter)
        self.today_tasks_list.setModel(self.today_tasks_model)
        self.today_tasks_list.setDragEnabled(True)
        self.today_tasks_list.setAcceptDrops(True)
        self.today_tasks_list.setDropIndicatorShown(True)
        self.today_tasks_list.setDefaultDropAction(Qt.MoveAction)
        lists_layout.addWidget(self.today_tasks_label)
        lists_layout.addWidget(self.today_tasks_list)
        self.setLayout(lists_layout)

        self.page_loaded.connect(self.on_page_loaded)

        # Émettre le signal page_loaded
        self.page_loaded.emit()

    def load_tasks(self):
        """
        Méthode pour charger les tâches du jour

        Args:
            None
        Returns:
            None
        """
        self.today_tasks_model.clear()
        self.cursor.execute("SELECT * FROM tasks WHERE end_date = ?", (QDate.currentDate().toString("dd-MM-yy"),))
        tasks = self.cursor.fetchall()

        for task in tasks:
            item = QStandardItem(task[1])
            self.today_tasks_model.appendRow(item)

    def on_page_loaded(self):
        """
        Méthode pour charger les tâches du jour

        Args:
            None
        Returns:
            None
        """
        self.load_tasks()
