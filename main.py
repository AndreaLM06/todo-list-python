import sys
from PySide6.QtWidgets import QApplication
from todo_list import TodoApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = TodoApp()
    mainWin.show()
    sys.exit(app.exec())
