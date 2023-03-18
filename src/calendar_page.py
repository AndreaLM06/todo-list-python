from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton

from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import Qt


class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.tasks = tasks

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        painter.setPen(Qt.black)
        painter.drawRect(rect)

        text = self.cell_text(date)
        if text:
            painter.setPen(Qt.black)
            new_rect = rect.adjusted(0, 0, 0, -rect.height() // 2)
            painter.drawText(new_rect, Qt.AlignLeft | Qt.TextWordWrap, text)

    def cell_text(self, date):
        task_date = QDate.toString(date, "dd-MM-yy")
        if task_date in self.tasks:
            tasks = self.tasks[task_date]
            task_text = " - ".join(tasks)
            return task_text
        else:
            return ""


class CalendarPage(QWidget):
    page_loaded = Signal()

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.init_ui()

    def init_ui(self):
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

        self.back_button = QPushButton("Changer de page (ToDo List)")
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # Connecter le signal clicked du bouton retour à la méthode back_to_list
        self.back_button.clicked.connect(self.page_loaded.emit)

        self.switch_page_button = QPushButton("Changer de page (Calendrier)")

        # Émettre le signal page_loaded
        self.page_loaded.emit()

    def back_to_list(self):
        self.parent().switch_page()

    def load_tasks(self):
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

    def update_calendar(self):
        self.load_tasks()
        self.calendar.tasks = self.tasks
        self.calendar.updateCells()
