import sys
from PySide6.QtWidgets import QApplication
from todo_list import TodoApp

"""
    This is the main file of the application.
    It creates the application and the main window.
"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = TodoApp()
    mainWin.show()
    sys.exit(app.exec())
