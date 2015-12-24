from PyQt5.QtWidgets import QMainWindow, QMessageBox

from app.settings import get_settings
from app.ui.ui_main import Ui_MainWindow

ABOUT_HTML = ('<html><head/><body>'
              '<p><span style=" font-size:18pt;">KrakSat 2016</span><br/>'
              'Ground Station Software</p>'
              '<p><a href="http://cansat.kraksat.pl">cansat.kraksat.pl</a></p>'
              '<p>Copyright (c) 2015<br />'
              'KrakSat Team in CanSat 2016</p>'
              '</body></html>')


class MainWindow(QMainWindow, Ui_MainWindow):
    CONFIG_GEOMETRY_KEY = 'mainWindow/geometry'
    CONFIG_STATE_KEY = 'mainWindow/state'

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        settings = get_settings()
        self.restoreGeometry(settings.value(self.CONFIG_GEOMETRY_KEY))
        self.restoreState(settings.value(self.CONFIG_STATE_KEY))

        docks = (self.logsDock, self.queueDock, self.statisticsDock,
                 self.cameraDock)
        for dock in docks:
            self.menuView.addAction(dock.toggleViewAction())

    def show_about(self):
        QMessageBox().about(self, 'About KrakSat 2016 Ground Station Software',
                            ABOUT_HTML)

    def closeEvent(self, QCloseEvent):
        settings = get_settings()
        settings.setValue(self.CONFIG_GEOMETRY_KEY, self.saveGeometry())
        settings.setValue(self.CONFIG_STATE_KEY, self.saveState())
