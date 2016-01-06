from PyQt5.QtWidgets import QDockWidget

from app.ui.ui_camera import Ui_CameraDock


class CameraDock(QDockWidget, Ui_CameraDock):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
