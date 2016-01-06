from PyQt5.QtWidgets import QDockWidget

from app.ui.ui_missionstatus import Ui_MissionStatusDock


class MissionStatusDock(QDockWidget, Ui_MissionStatusDock):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
