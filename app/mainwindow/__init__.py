import logging
import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFrame

from app.gsinfodialog import GSInfoDialog
from app.mainwindow.camera import CameraDock
from app.mainwindow.logs import LogsDock
from app.mainwindow.missionstatus import MissionStatusDock
from app.mainwindow.parser import ParserDock
from app.mainwindow.queue import QueueDock
from app.mainwindow.statistics import StatisticsDock
from app.settings import Settings
from app.ui.ui_main import Ui_MainWindow

with open(os.path.join(os.path.dirname(__file__), 'about.html')) as f:
    ABOUT_HTML = f.read().strip()


class MainWindow(QMainWindow, Ui_MainWindow):
    CONFIG_GEOMETRY_KEY = 'mainWindow/geometry'
    CONFIG_STATE_KEY = 'mainWindow/state'

    def __init__(self, sender, parser_manager):
        """Constructor

        :param app.sender.QtSender sender: QtSender instance to use with
            QueueTableModel
        :param parser_manager: ParserManager instance to use with ParserDock
        :type parser_manager: app.parser.outputparser.ParserManager
        """
        super(MainWindow, self).__init__()
        self._sender = sender
        self._parser_manager = parser_manager
        self.setupUi(self)

        self.webview_go_home()
        self._init_docks()
        settings = Settings()
        self.restoreGeometry(settings[self.CONFIG_GEOMETRY_KEY])
        self.restoreState(settings[self.CONFIG_STATE_KEY])
        self._init_statusbar()

        logging.getLogger('mainwindow').info("Main Window initialized")

    def _init_docks(self):
        self.logsDock = LogsDock(self)
        self.parserDock = ParserDock(self, self._parser_manager)
        self.queueDock = QueueDock(self, self._sender)
        self.statisticsDock = StatisticsDock(self, self._sender)
        self.cameraDock = CameraDock(self)
        self.missionStatusDock = MissionStatusDock(self, self._sender)
        docks = {
            Qt.LeftDockWidgetArea: (
                self.statisticsDock,
                self.queueDock,
                self.cameraDock,
                self.missionStatusDock,
            ),
            Qt.BottomDockWidgetArea: (
                self.logsDock,
                self.parserDock
            )
        }
        for area, dock_list in docks.items():
            for dock in dock_list:
                self.addDockWidget(area, dock)
                self.menuView.addAction(dock.toggleViewAction())

    def _init_statusbar(self):
        self.statusBar().addPermanentWidget(
                self.parserDock.create_statusbar_widget())
        self.statusBar().addPermanentWidget(self._create_statusbar_separator())
        self.statusBar().addPermanentWidget(
                self.queueDock.create_statusbar_widget())

    def _create_statusbar_separator(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.VLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame

    def show_set_gs_info(self):
        GSInfoDialog(self._sender, self).show()

    def show_about(self):
        QMessageBox().about(self, 'About KrakSat 2016 Ground Station Software',
                            ABOUT_HTML)

    def webview_go_home(self):  # you are drunk
        # todo set to our equivalent of live.techswarm.org as soon as it runs
        self.webView.setUrl(QUrl('http://cansat.kraksat.pl'))

    def closeEvent(self, event):
        settings = Settings()
        settings[self.CONFIG_GEOMETRY_KEY] = self.saveGeometry()
        settings[self.CONFIG_STATE_KEY] = self.saveState()
        self.logsDock.save_settings()
