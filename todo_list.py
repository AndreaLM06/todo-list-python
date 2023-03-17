from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton,
                               QListView, QLabel, QDateEdit, QMessageBox, QInputDialog, QDialog, QGroupBox,
                               QRadioButton, QDialogButtonBox, QTextEdit, QCheckBox)
import sqlite3
from datetime import datetime


class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.end_date_value = None
        self.end_date = None
        self.start_date_value = None
        self.start_date = None
        self.title = None
        self.urgent = None
        self.task_input = None

        self.filter_option = None
        self.sort_option = None

        self.init_ui()
        self.init_db()

    def init_ui(self):
        self.setWindowTitle("Todo List")

        main_layout = QVBoxLayout()

        self.task_input = QLineEdit()
        main_layout.addWidget(self.task_input)

        date_layout = QHBoxLayout()
        self.start_date = QLabel("Date d'ajout (dd-mm-yy) :")
        self.start_date_value = QDateEdit()
        self.start_date_value.setDate(datetime.today())
        self.start_date_value.setDisplayFormat("dd-MM-yy")
        self.start_date_value.setReadOnly(True)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.start_date_value)

        self.end_date = QLabel("Date de fin prévisionnelle (dd-mm-yy) :")
        self.end_date_value = QDateEdit()
        self.end_date_value.setDate(self.start_date_value.date().addDays(1))
        self.end_date_value.setDisplayFormat("dd-MM-yy")
        date_layout.addWidget(self.end_date)
        date_layout.addWidget(self.end_date_value)

        main_layout.addLayout(date_layout)

        self.add_task_button = QPushButton("Ajouter tâche")
        main_layout.addWidget(self.add_task_button)

        lists_layout = QHBoxLayout()

        self.todo_model = QStandardItemModel()
        self.done_model = QStandardItemModel()

        # To Do List
        todo_layout = QVBoxLayout()
        self.todo_label = QLabel("To Do")
        self.todo_label.setAlignment(Qt.AlignHCenter)
        self.todo_list = QListView()
        self.todo_list.setModel(self.todo_model)
        todo_layout.addWidget(self.todo_label)
        todo_layout.addWidget(self.todo_list)
        lists_layout.addLayout(todo_layout)

        # Done List
        done_layout = QVBoxLayout()
        self.done_label = QLabel("Done")
        self.done_label.setAlignment(Qt.AlignHCenter)
        self.done_list = QListView()
        self.done_list.setModel(self.done_model)
        done_layout.addWidget(self.done_label)
        done_layout.addWidget(self.done_list)
        lists_layout.addLayout(done_layout)

        main_layout.addLayout(lists_layout)

        # Remove Task Button
        self.remove_task_button = QPushButton("Supprimer tâche")
        main_layout.addWidget(self.remove_task_button)

        # Filter and Sort Button
        self.filter_and_sort_button = QPushButton("Filtrer et trier")
        main_layout.addWidget(self.filter_and_sort_button)

        # Edit Task Button
        self.edit_task_button = QPushButton("Modifier tâche")
        main_layout.addWidget(self.edit_task_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)
        self.edit_task_button.clicked.connect(self.edit_task)
        self.filter_and_sort_button.clicked.connect(self.show_filter_and_sort_dialog)

        self.add_task_button.clicked.disconnect(self.add_task)
        self.add_task_button.clicked.connect(self.show_add_task_dialog)

        self.todo_list.doubleClicked.connect(self.move_to_done)

    def show_add_task_dialog(self):
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

        end_date_label = QLabel("Date de fin prévisionnelle (dd-mm-yy) :")
        vbox.addWidget(end_date_label)

        end_date_input = QDateEdit()
        end_date_input.setDate(self.start_date_value.date().addDays(1))
        end_date_input.setDisplayFormat("dd-MM-yy")
        vbox.addWidget(end_date_input)

        urgent_label = QLabel("Urgent :")
        vbox.addWidget(urgent_label)

        urgent_checkbox = QCheckBox()
        vbox.addWidget(urgent_checkbox)

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
            urgent = urgent_checkbox.isChecked()
            self.add_task(title, description, end_date, urgent)

    def add_task(self, title, description, end_date, urgent):
        start_date = self.start_date_value.date().toString("dd-MM-yy")
        if title:
            item = QStandardItem(f"{title} (Ajouté le {start_date}, fin prévue le {end_date})")
            if urgent:
                item.setBackground(Qt.red)
            self.todo_model.appendRow(item)

            # Ajouter la tâche à la base de données
            self.cursor.execute(
                "INSERT INTO tasks (task, description, start_date, end_date, status, urgent) VALUES (?, ?, ?, ?, ?, ?)",
                (title, description, start_date, end_date, 'todo', urgent))
            self.conn.commit()

    def remove_task(self):
        # Remove the selected task from the To Do list
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

    def move_to_done(self, index):
        if index.isValid():
            item = self.todo_model.itemFromIndex(index).clone()
            self.todo_model.removeRow(index.row())
            self.done_model.appendRow(item)

            task = item.text().split(" (Ajouté le ")[0]
            self.cursor.execute("UPDATE tasks SET status = ? WHERE task = ?", ('done', task))
            self.conn.commit()

    def edit_task(self):
        index = self.todo_list.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une tâche à modifier.")
            return

        task = self.todo_model.itemFromIndex(index).text().split(" (Ajouté le ")[0]
        new_task, ok = QInputDialog.getText(self, "Modifier tâche", "Entrez le nouveau nom de la tâche :",
                                            QLineEdit.Normal, task)
        if ok and new_task != '':
            # Update task in the database
            self.cursor.execute("UPDATE tasks SET task = ? WHERE task = ? AND status = ?", (new_task, task, 'todo'))
            self.conn.commit()

            # Update task in the model
            start_date, end_date = get_dates_from_item(self.todo_model.itemFromIndex(index).text())
            item = QStandardItem(f"{new_task} (Ajouté le {start_date}, fin prévue le {end_date})")
            self.todo_model.setItem(index.row(), item)

    def show_filter_and_sort_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Filtrer et trier")

        vbox = QVBoxLayout()

        filter_group = QGroupBox("Filtrer")
        filter_layout = QVBoxLayout()

        self.show_all_radio = QRadioButton("Afficher tout")
        self.show_all_radio.setChecked(self.filter_option == "all")
        self.show_all_radio.toggled.connect(lambda: self.set_filter_option("all"))
        self.show_upcoming_radio = QRadioButton("Afficher seulement les tâches à venir")
        self.show_upcoming_radio.setChecked(self.filter_option == "upcoming")
        self.show_upcoming_radio.toggled.connect(lambda: self.set_filter_option("upcoming"))
        filter_layout.addWidget(self.show_all_radio)
        filter_layout.addWidget(self.show_upcoming_radio)
        filter_group.setLayout(filter_layout)
        vbox.addWidget(filter_group)

        sort_group = QGroupBox("Trier")
        sort_layout = QVBoxLayout()

        self.sort_by_start_date_radio = QRadioButton("Trier par date d'ajout")
        self.sort_by_start_date_radio.setChecked(self.sort_option == "start_date")
        self.sort_by_start_date_radio.toggled.connect(lambda: self.set_sort_option("start_date"))
        self.sort_by_end_date_radio = QRadioButton("Trier par date de fin prévisionnelle")
        self.sort_by_end_date_radio.setChecked(self.sort_option == "end_date")
        self.sort_by_end_date_radio.toggled.connect(lambda: self.set_sort_option("end_date"))
        sort_layout.addWidget(self.sort_by_start_date_radio)
        sort_layout.addWidget(self.sort_by_end_date_radio)
        sort_group.setLayout(sort_layout)
        vbox.addWidget(sort_group)

        reset_button = QPushButton("Réinitialiser les filtres")
        reset_button.clicked.connect(self.reset_filters)
        vbox.addWidget(reset_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        dialog.setLayout(vbox)

        result = dialog.exec()

        if result == QDialog.Accepted:
            self.apply_filter_and_sort()
        else:
            self.load_tasks()

    def set_filter_option(self, option):
        self.filter_option = option

    def set_sort_option(self, option):
        self.sort_option = option

    def reset_filters(self):
        self.filter_option = None
        self.sort_option = None

        self.show_all_radio.setChecked(True)
        self.show_upcoming_radio.setChecked(False)
        self.sort_by_start_date_radio.setChecked(False)
        self.sort_by_end_date_radio.setChecked(False)

    def apply_filter_and_sort(self):
        self.load_tasks(self.filter_option, self.sort_option)

    def init_db(self):
        self.conn = sqlite3.connect("todo.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                task TEXT NOT NULL,
                                                description TEXT,
                                                start_date TEXT NOT NULL,
                                                end_date TEXT,
                                                status TEXT NOT NULL,
                                                urgent INTEGER NOT NULL)''')
        self.conn.commit()
        self.load_tasks()

    def load_tasks(self, filter_option=None, sort_option=None):
        query = "SELECT task, start_date, end_date, status FROM tasks"
        params = []

        if filter_option == "upcoming":
            query += " WHERE end_date >= ?"
            params.append(datetime.today().strftime("%d-%m-%y"))

        if sort_option == "start_date":
            query += " ORDER BY start_date"
        elif sort_option == "end_date":
            query += " ORDER BY end_date"

        self.cursor.execute(query, params)
        tasks = self.cursor.fetchall()

        self.todo_model.clear()
        self.done_model.clear()

        for task in tasks:
            item = QStandardItem(
                f"{task[0]} (Ajouté le {task[1]}, fin prévue le {task[2]})")
            if task[3] == "todo":
                self.todo_model.appendRow(item)
            else:
                self.done_model.appendRow(item)

    def set_filter_option(self, option):
        self.filter_option = option


def get_dates_from_item(item_text):
    start_date = item_text.split(" (Ajouté le ")[1].split(", fin prévue le ")[0]
    end_date = item_text.split(", fin prévue le ")[1].split(")")[0]
    return start_date, end_date
