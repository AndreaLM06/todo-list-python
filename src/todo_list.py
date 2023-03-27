from calendar_page import CalendarPage

from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton,
                               QListView, QLabel, QDateEdit, QMessageBox, QInputDialog, QDialog, QDialogButtonBox,
                               QTextEdit, QStackedWidget, QMenuBar)
import sqlite3
from datetime import datetime

from today_task_page import TodayTaskPage
from task_model import TaskModel


class TodoApp(QMainWindow):
    task_added = Signal()
    task_modified = Signal()
    task_removed = Signal(str, str)

    def __init__(self):
        super().__init__()

        self.switch_to_calendar_action = None
        self.switch_to_todo_action = None
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

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle("TaskMaster")

        main_layout = QVBoxLayout()
        lists_layout = QVBoxLayout()

        # Menu Bar
        # Create the menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # Create the TodoList action and add it to the menu
        todo_list_action = QAction(" Todo List ", self)
        todo_list_action.triggered.connect(self.show_todo_list_page)
        menubar.addAction(todo_list_action)

        # Create the Calendar action and add it to the menu
        calendar_action = QAction(" Calendar ", self)
        calendar_action.triggered.connect(self.show_calendar_page)
        menubar.addAction(calendar_action)

        # Create the TodayTask action and add it to the menu
        today_task_action = QAction(" Task of the day ", self)
        today_task_action.triggered.connect(self.show_today_task_page)
        menubar.addAction(today_task_action)

        # Create the Quit action and add it to the menu
        quit_action = QAction(" Quit ", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        menubar.addAction(quit_action)

        self.start_date_value.setDate(datetime.today())
        self.start_date_value.setDisplayFormat("dd-MM-yy")
        self.end_date = QLabel("Estimated end date (dd-mm-yy) :")
        self.end_date_value.setDate(self.start_date_value.date().addDays(1))
        self.end_date_value.setDisplayFormat("dd-MM-yy")

        self.todo_model = TaskModel()
        self.done_model = TaskModel()

        # To Do List
        self.todo_label = QLabel("To Do")
        self.todo_label.setAlignment(Qt.AlignHCenter)
        self.todo_list = QListView()
        self.todo_list.setModel(self.todo_model)
        self.todo_list.setDragEnabled(True)
        self.todo_list.setAcceptDrops(True)
        self.todo_list.setDropIndicatorShown(True)
        self.todo_list.setDefaultDropAction(Qt.MoveAction)
        lists_layout.addWidget(self.todo_label)
        lists_layout.addWidget(self.todo_list)

        # Done List
        self.done_label = QLabel("Done")
        self.done_label.setAlignment(Qt.AlignHCenter)
        self.done_list = QListView()
        self.done_list.setModel(self.done_model)
        self.done_list.setDragEnabled(True)
        self.done_list.setAcceptDrops(True)
        self.done_list.setDropIndicatorShown(True)
        self.done_list.setDefaultDropAction(Qt.MoveAction)
        lists_layout.addWidget(self.done_label)
        lists_layout.addWidget(self.done_list)

        main_layout.addLayout(lists_layout)

        # Add Task Button
        self.add_task_button = QPushButton("Add task")
        main_layout.addWidget(self.add_task_button)

        # Edit Task Button
        self.edit_task_button = QPushButton("Edit task")
        main_layout.addWidget(self.edit_task_button)

        # Remove Task Button
        self.remove_task_button = QPushButton("Delete task")
        main_layout.addWidget(self.remove_task_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)
        self.edit_task_button.clicked.connect(self.edit_task)

        self.add_task_button.clicked.disconnect(self.add_task)
        self.add_task_button.clicked.connect(self.show_add_task_dialog)

        self.edit_task_button.clicked.disconnect(self.edit_task)
        self.edit_task_button.clicked.connect(self.show_edit_task_dialog)

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

        self.today_task_page = TodayTaskPage(self.conn)
        self.today_task_page.load_tasks()

        self.stacked_widget.addWidget(self.todo_page)
        self.stacked_widget.addWidget(self.calendar_page)
        self.stacked_widget.addWidget(self.today_task_page)

        self.setCentralWidget(self.stacked_widget)

        self.task_added.connect(self.calendar_page.update_calendar)
        self.task_modified.connect(self.calendar_page.update_calendar)
        self.task_removed.connect(self.calendar_page.remove_task)

        self.task_added.connect(self.today_task_page.load_tasks)
        self.task_modified.connect(self.today_task_page.load_tasks)

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

    def show_edit_task_dialog(self):
        """
        Show the edit task dialog

        Args:
            None

        Returns:
            None
        """
        index = self.todo_list.currentIndex()
        task = self.todo_model.itemFromIndex(index).text()
        title = task.split(", ")[0]
        end_task = task.split(", (")[1].split(")")[0] #25-03-23
        # mais on veut mette la date au format 25/03/2023
        end_task = QDate.fromString(end_task, "dd-MM-yy") # 25-03-23
        end_task = end_task.addYears(100) # 25-03-23
        print(end_task) # PySide6.QtCore.QDate(1923, 3, 25)

        print(task) # test2, (25-03-23)
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier une tâche")

        vbox = QVBoxLayout()

        title_label = QLabel("Titre de la tâche :")
        vbox.addWidget(title_label)

        title_input = QLineEdit()
        title_input.setText(title)
        vbox.addWidget(title_input)

        description_label = QLabel("Description :")
        vbox.addWidget(description_label)

        description_input = QTextEdit()
        vbox.addWidget(description_input)

        end_date_label = QLabel("Date de fin prévisionnelle (dd-mm-yyyy) :")

        end_date_input = QDateEdit()
        end_date_input.setCalendarPopup(True)

        today = QDate.currentDate()
        end_date_input.setDate(end_task)

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

    def add_task(self, title, description, end_date):
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
            self.task_added.emit()
            self.update_calendar()
            self.update_today_task()

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
            end_date = task.split(", (")[1].split(")")[0]
            self.task_removed.emit(task, end_date)

            # Remove the selected task from the Done list
        index = self.done_list.currentIndex()
        if index.isValid():
            task = self.done_model.itemFromIndex(index).text().split(" (Ajouté le ")[0]
            self.cursor.execute("DELETE FROM tasks WHERE task = ? AND status = ?", (task, 'done'))
            self.conn.commit()
            self.done_model.removeRow(index.row())
            self.update_today_task()
            end_date = task.split(", (")[1].split(")")[0]
            self.task_removed.emit(task, end_date)
        self.update_calendar()
        self.today_task_page.load_tasks()

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
            self.task_modified.emit()
        self.update_calendar()
        self.update_today_task()

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
        """
        Save tasks from the ToDo and Done lists to the database

        Args:
            None

        Returns:
            None
        """
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

    def update_calendar(self):
        self.calendar_page.load_tasks()

    def update_today_task(self):
        self.today_task_page.load_tasks()

    def show_todo_list_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_calendar_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_today_task_page(self):
        self.stacked_widget.setCurrentIndex(2)


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
