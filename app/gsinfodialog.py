from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from app.ui.ui_gsinfo import Ui_GSInfoDialog


class GSInfoDialog(QDialog, Ui_GSInfoDialog):
    """Set Ground Station info dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.loginButton = self.buttonBox.addButton(
                "&Submit", QDialogButtonBox.AcceptRole)
