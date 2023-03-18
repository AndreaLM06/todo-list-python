from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QStandardItemModel


class TaskModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

    def mimeTypes(self):
        return ["text/plain"]

    def supportedDropActions(self):
        return Qt.MoveAction

    def flags(self, index):
        if index.isValid():
            return super().flags(index) | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        else:
            return super().flags(index) | Qt.ItemIsDropEnabled
