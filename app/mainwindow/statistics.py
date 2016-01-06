from PyQt5.QtWidgets import QDockWidget

from app.ui.ui_statistics import Ui_StatisticsDock


class StatisticsDock(QDockWidget, Ui_StatisticsDock):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
