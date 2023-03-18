from calendar_page import CalendarPage

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton,
                               QListView, QLabel, QDateEdit, QMessageBox, QInputDialog, QDialog, QDialogButtonBox,
                               QTextEdit, QStackedWidget)
import sqlite3
from datetime import datetime

from task_model import TaskModel


class TodoApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.switch_page_button = None
        self.calendar_page = None
        self.todo_page = None
        self.stacked_widget = None
        self.calendar = None
        self.end_date_input = None
        self.sort_by_end_date_radio = None
        self.show_all_radio = None
        self.edit_task_button = None
        self.filter_and_sort_button = None
        self.cursor = None
        self.conn = None
        self.done_model = None
        self.todo_model = None
        self.remove_task_button = None
        self.done_list = None
        self.done_label = None
        self.todo_list = None
        self.todo_label = None
        self.add_task_button = None
        self.end_date_value = QDateEdit()
        self.end_date = None
        self.start_date_value = QDateEdit()
        self.start_date = None
        self.title = None
        self.task_input = None

        self.filter_option = None
        self.sort_option = None

        self.init_ui()
        self.init_db()

        self.todo_model.rowsInserted.connect(self.task_moved)
        self.todo_model.rowsRemoved.connect(self.task_moved)
        self.done_model.rowsInserted.connect(self.task_moved)
        self.done_model.rowsRemoved.connect(self.task_moved)

        self.calendar_page = CalendarPage(self.conn)
        self.calendar_page.page_loaded.connect(self.calendar_page.load_tasks)

        self.calendar_page.page_loaded.connect(self.update_calendar)

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle("TaskMaster")

        main_layout = QVBoxLayout()

        self.start_date_value.setDate(datetime.today())
        self.start_date_value.setDisplayFormat("dd-MM-yy")

        self.end_date = QLabel("Date de fin prévisionnelle (dd-mm-yy) :")
        self.end_date_value.setDate(self.start_date_value.date().addDays(1))
        self.end_date_value.setDisplayFormat("dd-MM-yy")

        self.add_task_button = QPushButton("Ajouter tâche")
        main_layout.addWidget(self.add_task_button)

        lists_layout = QHBoxLayout()

        self.todo_model = TaskModel()
        self.done_model = TaskModel()

        # To Do List
        todo_layout = QVBoxLayout()
        self.todo_label = QLabel("To Do")
        self.todo_label.setAlignment(Qt.AlignHCenter)
        self.todo_list = QListView()
        self.todo_list.setModel(self.todo_model)
        self.todo_list.setDragEnabled(True)
        self.todo_list.setAcceptDrops(True)
        self.todo_list.setDropIndicatorShown(True)
        self.todo_list.setDefaultDropAction(Qt.MoveAction)
        todo_layout.addWidget(self.todo_label)
        todo_layout.addWidget(self.todo_list)
        lists_layout.addLayout(todo_layout)

        # Done List
        done_layout = QVBoxLayout()
        self.done_label = QLabel("Done")
        self.done_label.setAlignment(Qt.AlignHCenter)
        self.done_list = QListView()
        self.done_list.setModel(self.done_model)
        self.done_list.setDragEnabled(True)
        self.done_list.setAcceptDrops(True)
        self.done_list.setDropIndicatorShown(True)
        self.done_list.setDefaultDropAction(Qt.MoveAction)
        done_layout.addWidget(self.done_label)
        done_layout.addWidget(self.done_list)
        lists_layout.addLayout(done_layout)

        main_layout.addLayout(lists_layout)

        # Remove Task Button
        self.remove_task_button = QPushButton("Supprimer tâche")
        main_layout.addWidget(self.remove_task_button)

        # Edit Task Button
        self.edit_task_button = QPushButton("Modifier tâche")
        main_layout.addWidget(self.edit_task_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)
        self.edit_task_button.clicked.connect(self.edit_task)

        self.add_task_button.clicked.disconnect(self.add_task)
        self.add_task_button.clicked.connect(self.show_add_task_dialog)

        self.todo_model.rowsInserted.connect(self.task_moved)
        self.todo_model.rowsRemoved.connect(self.task_moved)
        self.done_model.rowsInserted.connect(self.task_moved)
        self.done_model.rowsRemoved.connect(self.task_moved)

        self.stacked_widget = QStackedWidget()

        self.todo_page = QWidget()
        self.todo_page.setLayout(main_layout)

        self.init_db()

        self.calendar_page = CalendarPage(self.conn)
        self.calendar_page.load_tasks()

        self.stacked_widget.addWidget(self.todo_page)
        self.stacked_widget.addWidget(self.calendar_page)

        self.setCentralWidget(self.stacked_widget)

        self.switch_page_button = QPushButton("Changer de page (Calendrier)")
        self.switch_page_button.clicked.connect(self.switch_page)

        self.calendar_page.page_loaded.connect(self.switch_page)

        main_layout.addWidget(self.switch_page_button)

    def task_moved(self, parent, start, end):
        """
        Update the database when a task is moved between ToDo and Done lists

        Args:
            parent (QModelIndex): The parent model index
            start (int): The starting row
            end (int): The ending row

        Returns:
            None
        """
        sender = self.sender()
        if sender == self.todo_model:
            new_status = "todo"
        else:
            new_status = "done"

        for row in range(start, end + 1):
            item = sender.item(row)
            if item is not None:  # Check if the item exists
                task_title = item.text().split(", ")[0]
                self.cursor.execute("UPDATE tasks SET status = ? WHERE task = ?", (new_status, task_title))
                self.conn.commit()

    def update_task_status(self, task, new_status):
        """
        Update the status of the task in the database

        Args:
            task (str): The task to update
            new_status (str): The new status of the task ('todo' or 'done')

        Returns:
            None
        """
        self.cursor.execute("UPDATE tasks SET status = ? WHERE task = ?", (new_status, task))
        self.conn.commit()

    def on_rows_moved(self, source_model, target_model, index):
        """
        Handle rows moved between the ToDo and Done lists

        Args:
            source_model (QStandardItemModel): The source model where the row was moved from
            target_model (QStandardItemModel): The target model where the row was moved to
            index (QModelIndex): The index of the moved row in the target model

        Returns:
            None
        """
        if source_model != target_model:
            task = target_model.itemFromIndex(index).text().split(" (Ajouté le ")[0]
            new_status = 'done' if target_model == self.done_model else 'todo'
            self.update_task_status(task, new_status)

    def show_add_task_dialog(self):
        """
        Show the add task dialog

        Args:
            None

        Returns:
            None
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une tâche")

        vbox = QVBoxLayout()

        title_label = QLabel("Titre de la tâche :")
        vbox.addWidget(title_label)

        title_input = QLineEdit()
        vbox.addWidget(title_input)

        description_label = QLabel("Description :")
        vbox.addWidget(description_label)

        description_input = QTextEdit()
        vbox.addWidget(description_input)

        end_date_label = QLabel("Date de fin prévisionnelle (dd-mm-yyyy) :")

        end_date_input = QDateEdit()
        end_date_input.setCalendarPopup(True)

        today = QDate.currentDate()
        end_date_input.setDate(today)

        vbox.addWidget(end_date_label)
        vbox.addWidget(end_date_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        dialog.setLayout(vbox)

        result = dialog.exec()

        if result == QDialog.Accepted:
            title = title_input.text()
            description = description_input.toPlainText()
            end_date = end_date_input.date().toString("dd-MM-yy")
            self.add_task(title, description, end_date)

    def add_task(self, title, description, end_date) -> None:
        """
        Add a task to the To Do list
        Args:
            title (str): The title of the task
            description (str): The description of the task
            end_date (str): The end date of the task

        Returns:
            None
        """
        if title:
            item = QStandardItem(f"{title}, ({end_date})")
            self.todo_model.appendRow(item)

            # Ajouter la tâche à la base de données
            self.cursor.execute(
                "INSERT INTO tasks (task, description, end_date, status) VALUES ( ?, ?, ?, ?)",
                (title, description, end_date, 'todo'))
            self.conn.commit()

            end_date_qdate = QDate.fromString(end_date, "dd-MM-yy")
            self.calendar_page.add_task(title, end_date_qdate)
        self.update_calendar()

    def remove_task(self):
        """
        Remove the selected task from the To Do list or the Done list

        Args:
            None

        Returns:
            None
        """
        index = self.todo_list.currentIndex()
        if index.isValid():
            task = self.todo_model.itemFromIndex(index).text().split(" (Ajouté le ")[0]
            self.cursor.execute("DELETE FROM tasks WHERE task = ? AND status = ?", (task, 'todo'))
            self.conn.commit()
            self.todo_model.removeRow(index.row())

        # Remove the selected task from the Done list
        index = self.done_list.currentIndex()
        if index.isValid():
            task = self.done_model.itemFromIndex(index).text().split(" (Ajouté le ")[0]
            self.cursor.execute("DELETE FROM tasks WHERE task = ? AND status = ?", (task, 'done'))
            self.conn.commit()
            self.done_model.removeRow(index.row())
        self.update_calendar()

    def edit_task(self):
        """
        Edit the selected task

        Args:
            None

        Returns:
            None
        """
        index = self.todo_list.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une tâche à modifier.")
            return

        task = self.todo_model.itemFromIndex(index).text().split(", (")[0]
        new_task, ok = QInputDialog.getText(self, "Modifier tâche", "Entrez le nouveau nom de la tâche :",
                                            QLineEdit.Normal, task)
        if ok and new_task != '':
            # Update task in the database
            self.cursor.execute("UPDATE tasks SET task = ? WHERE task = ? AND status = ?", (new_task, task, 'todo'))
            self.conn.commit()

            # Update task in the model

            end_date = get_dates_from_item(self.todo_model.itemFromIndex(index).text())
            item = QStandardItem(f"{new_task}, ({end_date})")
            self.todo_model.setItem(index.row(), item)
        self.update_calendar()

    def init_db(self):
        """
        Initialize the database

        Args:
            None

        Returns:
            None
        """
        self.conn = sqlite3.connect("../todo.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                task TEXT NOT NULL,
                                                description TEXT,                                    
                                                end_date TEXT,
                                                status TEXT NOT NULL)''')
        self.conn.commit()
        self.load_tasks()

    def load_tasks(self):
        """
        Load tasks from the database and display them in the ToDo or Done lists

        Returns:
            None
        """
        if self.todo_model is not None and self.done_model is not None:
            self.todo_model.clear()
            self.done_model.clear()

        self.cursor.execute("SELECT task, status, end_date FROM tasks")
        tasks = self.cursor.fetchall()

        for task, status, end_date in tasks:
            item = QStandardItem(f"{task}, ({end_date})")
            item.setDropEnabled(False)

            if status == "todo":
                self.todo_model.appendRow(item)
            elif status == "done":
                self.done_model.appendRow(item)

        self.todo_list.setModel(self.todo_model)
        self.done_list.setModel(self.done_model)

    def set_filter_option(self, option):
        """
        Set the filter option

        Args:
            option (str): The filter option

        Returns:
            None
        """
        self.filter_option = option

    def save_tasks(self):
        # Delete all tasks from the database
        self.cursor.execute("DELETE FROM tasks")

        # Save tasks from ToDo list
        for index in range(self.todo_model.rowCount()):
            item = self.todo_model.item(index)
            task_title, end_date = get_details_from_item(item.text())
            self.cursor.execute("INSERT INTO tasks (task, status, end_date) VALUES (?, ?, ?)",
                                (task_title, "todo", end_date))

        # Save tasks from Done list
        for index in range(self.done_model.rowCount()):
            item = self.done_model.item(index)
            task_title, end_date = get_details_from_item(item.text())
            self.cursor.execute("INSERT INTO tasks (task, status, end_date) VALUES ( ?, ?, ?)",
                                (task_title, "done", end_date))

        # Commit changes and close the database connection
        self.conn.commit()

    def closeEvent(self, event):
        """
        Close the application and save tasks to the database

        Args:
            event (QCloseEvent): The close event

        Returns:
            None
        """
        self.save_tasks()
        self.conn.close()
        event.accept()

    def switch_page(self):
        current_index = self.stacked_widget.currentIndex()
        next_index = (current_index + 1) % self.stacked_widget.count()
        self.stacked_widget.setCurrentIndex(next_index)

        if next_index == 0:
            self.switch_page_button.setText("Changer de page (Calendrier)")
        else:
            self.switch_page_button.setText("Changer de page (Todo List)")

    def update_calendar(self):
        self.calendar_page.load_tasks()
        self.calendar_page.calendar.updateCells()


def get_details_from_item(item_text):
    task_title = item_text.split(", ")[0]
    end_date = get_dates_from_item(item_text)
    return task_title, end_date


def get_dates_from_item(item_text):
    """
    Get the start and end dates from the item text

    Args:
        item_text (str): The item text

    Returns:
        end_date (str): The end date
    """
    end_date = item_text.split(", (")[1].rstrip(")")
    return end_date
