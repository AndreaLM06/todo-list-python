from PySide6.QtGui import Qt, QFont, QPen
from PySide6.QtWidgets import QCalendarWidget, QVBoxLayout, QWidget, QPushButton

from PySide6.QtCore import Signal, QDate


class CalendarPage(QWidget):
    back_to_list_requested = Signal()

    def __init__(self, cursor):
        super().__init__()

        self.calendar = None
        self.back_button = None
        self.cursor = cursor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.back_button = QPushButton("Retour")
        layout.addWidget(self.back_button)

        self.calendar = Calendar()
        self.calendar.load_tasks(self.cursor)

        layout.addWidget(self.calendar)

        self.setLayout(layout)

        self.back_button.clicked.connect(self.back_to_list_requested.emit)

        self.switch_page_button = QPushButton("Changer de page (Calendrier)")


class Calendar(QCalendarWidget):
    def __init__(self, parent=None):
        super(Calendar, self).__init__(parent)
        self.tasks = {}

    def add_task(self, task, status, end_date):
        if end_date not in self.tasks:
            self.tasks[end_date] = []
        self.tasks[end_date].append({'task': task, 'status': status, 'end_date': end_date})

    def paintCell(self, painter, rect, date):
        super(Calendar, self).paintCell(painter, rect, date)

        if date in self.tasks:
            tasks = self.tasks[date]
            tasks.sort(key=lambda x: x['end_date'])

            # Set up the font and pen for drawing text
            font = QFont('Arial', 10)
            pen = QPen(Qt.SolidLine)
            pen.setWidth(2)
            painter.setFont(font)
            painter.setPen(pen)


    def load_tasks(self, cursor):
        if cursor is None:
            return

        cursor.execute("SELECT task, end_date, status FROM tasks WHERE status = 'todo'")
        tasks = cursor.fetchall()

        print(tasks)  # debug line

        for task, end_date, status in tasks:
            qdate = QDate.fromString(end_date, "dd-MM-yy")
            print(task)
            self.add_task(task, status, qdate)
