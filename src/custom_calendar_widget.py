from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import Qt


class CustomCalendarWidget(QCalendarWidget):
    """
    Classe pour le widget personnalisé du calendrier
    """

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.tasks = tasks

    def paintCell(self, painter, rect, date):
        """
        Méthode pour dessiner la cellule du calendrier

        Args:
            painter (QPainter): objet pour dessiner
            rect (QRect): rectangle de la cellule
            date (QDate): date de la cellule

        Returns:
            None
        """
        super().paintCell(painter, rect, date)

        painter.setPen(Qt.black)
        painter.drawRect(rect)

        text = self.cell_text(date)
        if text:
            painter.setPen(Qt.black)
            new_rect = rect.adjusted(0, 0, 0, -rect.height() // 2)
            painter.drawText(new_rect, Qt.AlignLeft | Qt.TextWordWrap, text)

    def cell_text(self, date):
        """
        Méthode pour obtenir le texte à afficher dans la cellule du calendrier

        Args:
            date (QDate): date de la cellule

        Returns:
            str: texte à afficher dans la cellule
        """
        task_date = QDate.toString(date, "dd-MM-yy")
        if task_date in self.tasks:
            tasks = self.tasks[task_date]
            task_text = " - ".join(tasks)
            return task_text
        else:
            return ""
