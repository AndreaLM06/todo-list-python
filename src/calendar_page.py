from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton

from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import Qt

from custom_calendar_widget import CustomCalendarWidget


class CalendarPage(QWidget):
    """
    Classe pour la page du calendrier de l'application
    """
    page_loaded = Signal()

    def __init__(self, conn):
        super().__init__()
        self.calendar = None
        self.tasks = None
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()

    def init_ui(self):
        """
        Méthode pour initialiser l'interface utilisateur de la page du calendrier
        :return:
        """
        layout = QVBoxLayout()

        self.load_tasks()
        self.calendar = CustomCalendarWidget(self.tasks)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Définir le format de la première colonne pour afficher le numéro de la date
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.ISOWeekNumbers)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Appliquer une mise en forme différente à la cellule du jour en cours
        today = QDate.currentDate()
        text_format = QTextCharFormat()
        text_format.setForeground(Qt.white)
        text_format.setBackground(Qt.green)
        self.calendar.setDateTextFormat(today, text_format)

        # Définir le premier jour de la semaine comme lundi
        self.calendar.setFirstDayOfWeek(Qt.Monday)

        layout.addWidget(self.calendar)

        self.setLayout(layout)

        self.page_loaded.connect(self.on_page_loaded)

        # Émettre le signal page_loaded
        self.page_loaded.emit()

    def load_tasks(self):
        """
        Méthode pour charger les tâches de la base de données
        :return:
        """
        self.tasks = {}  # dictionnaire pour stocker les tâches

        self.cursor.execute("SELECT task, end_date FROM tasks WHERE status = 'todo'")
        tasks = self.cursor.fetchall()

        for task, end_date in tasks:
            date = QDate.fromString(end_date, "dd-MM-yy")
            date_str = QDate.toString(date, "dd-MM-yy")

            if date_str not in self.tasks:
                self.tasks[date_str] = []
            self.tasks[date_str].append(task)

    def add_task(self, task, end_date):
        """
        Méthode pour ajouter une tâche à la base de données

        Args:
            task (str): tâche à ajouter
            end_date (QDate): date de fin de la tâche

        Returns:
            None
        """
        text_format = QTextCharFormat()
        text_format.setForeground(Qt.black)
        text_format.setFontWeight(QFont.Bold)
        text_format.setToolTip(task)
        text_format.setBackground(QColor(240, 240, 240))
        self.calendar.setDateTextFormat(end_date, text_format)

        if end_date not in self.tasks:
            self.tasks[end_date] = []
        self.tasks[end_date].append(task)
        self.calendar.tasks = self.tasks

    def remove_task(self, task, end_date):
        """
        Méthode pour supprimer une tâche de la base de données

        Args:
            task (str): tâche à supprimer
            end_date (QDate): date de fin de la tâche

        Returns:
            None
        """
        title_task = task.split(",")[0]
        self.delete_task_from_db(title_task)
        # self.tasks[end_date].remove(title_task)
        if not self.tasks[end_date]:
            del self.tasks[end_date]

        self.calendar.tasks = self.tasks
        self.calendar.updateCells()

    def update_calendar(self):
        """
        Méthode pour mettre à jour le calendrier

        Args:
            None

        Returns:
            None
        """
        self.load_tasks()
        self.calendar.tasks = self.tasks
        self.calendar.updateCells()

    def on_page_loaded(self):
        """
        Méthode pour mettre à jour le calendrier lorsque la page est chargée

        Args:
            None

        Returns:
            None
        """
        self.update_calendar()

    def delete_task_from_db(self, task):
        """
        Méthode pour supprimer une tâche de la base de données

        Args:
            task (str): tâche à supprimer

        Returns:
            None
        """
        self.cursor.execute("DELETE FROM tasks WHERE task = ?", (task,))
        self.conn.commit()
