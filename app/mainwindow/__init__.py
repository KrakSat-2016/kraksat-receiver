import logging
import os
from functools import partial

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QFrame, QFileDialog, QToolBar, QMenu,
    QApplication
)

from app.gsinfodialog import GSInfoDialog
from app.mainwindow.logs import LogsDock
from app.mainwindow.missionstatus import MissionStatusDock
from app.mainwindow.parser import QtParser
from app.mainwindow.queue import QueueDock
from app.mainwindow.statistics import StatisticsDock
from app.probestartdialog import ProbeStartDialog
from app.sender.sendererrorcatcher import QtSenderErrorCatcher
from app.settings import Settings
from app.ui.ui_main import Ui_MainWindow
from app.videoiddialog import VideoIDDialog

with open(os.path.join(os.path.dirname(__file__), 'about.html')) as f:
    ABOUT_HTML = f.read().strip()


class MainWindow(QMainWindow, Ui_MainWindow):
    CONFIG_GEOMETRY_KEY = 'mainWindow/geometry'
    CONFIG_STATE_KEY = 'mainWindow/state'
    CONFIG_LAST_FILE_KEY = 'mainWindow/lastFile'
    CONFIG_FILE_DIALOG_STATE_KEY = 'mainWindow/fileDialog/state'
    CONFIG_FILE_DIALOG_GEOMETRY_KEY = 'mainWindow/fileDialog/geometry'

    logger = logging.getLogger('MainWindow')

    def __init__(self, sender, parser_manager, analyzer_worker):
        """Constructor

        :param app.sender.QtSender sender: QtSender instance to use with
            QueueTableModel
        :param parser_manager: ParserManager instance to use with ParserDock
        :type parser_manager: app.parser.outputparser.ParserManager
        :param analyzer_worker: AnalyzerWorker instance to connect to the
            "Pause Analyzer" button to
        :type analyzer_worker: app.analyzer.AnalyzerWorker
        """
        super(MainWindow, self).__init__()
        self._sender = sender
        self._parser_manager = parser_manager
        self._analyzer_worker = analyzer_worker
        self.setupUi(self)
        self.sender_error_catcher = QtSenderErrorCatcher(self, sender)

        self.webapp_url = None
        self._init_docks()
        self._init_actions()
        self._init_toolbars()
        settings = Settings()
        if self.CONFIG_GEOMETRY_KEY in settings:
            self.restoreGeometry(settings[self.CONFIG_GEOMETRY_KEY])
        if self.CONFIG_STATE_KEY in settings:
            self.restoreState(settings[self.CONFIG_STATE_KEY])
        self._init_statusbar()

        self.logger.info("Main Window initialized")

    def _init_docks(self):
        self.logsDock = LogsDock(self)
        self.statisticsDock = StatisticsDock(self, self._sender,
                                             self._parser_manager)
        self.missionStatusDock = MissionStatusDock(self, self._sender)
        self.queueDock = QueueDock(self, self._sender)
        docks = {
            Qt.LeftDockWidgetArea: (
                self.statisticsDock,
                self.missionStatusDock,
                self.queueDock,
            ),
            Qt.BottomDockWidgetArea: (
                self.logsDock,
            )
        }
        for area, dock_list in docks.items():
            for dock in dock_list:
                self.addDockWidget(area, dock)
                self.menuView.addAction(dock.toggleViewAction())

    def _init_actions(self):
        self._parser_manager.parser_started.connect(
                partial(self.actionTerminateParser.setEnabled, True))
        self._parser_manager.parser_terminated.connect(
                partial(self.actionTerminateParser.setEnabled, False))
        self.actionTerminateParser.setEnabled(
                self._parser_manager.is_running())
        self._sender.queue_paused.connect(self.actionPauseQueue.setChecked)

    def _init_toolbars(self):
        self.menuView.addSeparator()
        self.toolbarsMenu = QMenu('&Toolbars')
        for toolbar in self.findChildren(QToolBar):
            self.toolbarsMenu.addAction(toolbar.toggleViewAction())
        self.menuView.addMenu(self.toolbarsMenu)

    def _init_statusbar(self):
        self.statusBar().addPermanentWidget(
                QtParser.create_statusbar_widget(self._parser_manager))
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

    def show_set_video_id(self):
        VideoIDDialog(self._sender, self).show()

    def show_set_probe_start_time(self):
        return ProbeStartDialog(self._parser_manager, self).exec()

    def show_about(self):
        QMessageBox().about(self, 'About KrakSat 2016 Ground Station Software',
                            ABOUT_HTML)

    def show_about_qt(self):
        QApplication.aboutQt()

    def set_webapp_url(self, url):
        """Set new webapp URL and load it in the web view

        :param str url: new webapp URL
        """
        self.webapp_url = url
        self.webview_go_home()

    def webview_go_home(self):  # ur drunk
        self.webView.load(QUrl(self.webapp_url))

    def terminate_parser(self):
        """Ask if user wants to terminate the parser and if so, terminate it

        :return: ``True`` if the parser was terminated; ``False`` if user
            clicked 'Cancel' button
        :rtype: bool
        """
        msg_box = QMessageBox(
                QMessageBox.Warning, 'Terminating the parser',
                'Are you sure you want to terminate the parser?',
                QMessageBox.Cancel)
        terminate_btn = msg_box.addButton('Terminate', QMessageBox.ActionRole)
        msg_box.exec()
        if msg_box.clickedButton() == terminate_btn:
            self._parser_manager.terminate()
            return True
        return False

    def set_queue_paused(self, paused):
        """Set whether or not the request queue will be paused"""
        self._sender.paused = paused

    def set_analyzer_paused(self, paused):
        self._analyzer_worker.paused = paused

    def set_processing_suspended(self, suspended):
        """Set whether or not processing the data will be suspended"""
        self._parser_manager.processing_suspended = suspended
        logging.getLogger('Analyzer').info(
            'Processing %s', 'suspended' if suspended else 'resumed')

    def choose_parser_file(self):
        if (self._parser_manager.probe_start_time is None and
                not self.show_set_probe_start_time()):
            return

        if self._parser_manager.is_running():
            msg_box = QMessageBox(
                    QMessageBox.Question, 'Parser is running',
                    'The parser is already running.', QMessageBox.Cancel)
            msg_box.setInformativeText('Do you want to terminate it?')
            terminate_btn = msg_box.addButton('Terminate',
                                              QMessageBox.ActionRole)
            msg_box.exec()
            if msg_box.clickedButton() == terminate_btn:
                self._parser_manager.terminate()
            else:
                return

        settings = Settings()
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle('Choose named pipe or output file')
        if self.CONFIG_LAST_FILE_KEY in settings:
            file_dialog.selectFile(settings[self.CONFIG_LAST_FILE_KEY])
        else:
            file_dialog.setDirectory(os.getcwd())
        if self.CONFIG_FILE_DIALOG_STATE_KEY in settings:
            file_dialog.restoreState(
                settings[self.CONFIG_FILE_DIALOG_STATE_KEY])
        if self.CONFIG_FILE_DIALOG_GEOMETRY_KEY in settings:
            file_dialog.restoreGeometry(
                settings[self.CONFIG_FILE_DIALOG_GEOMETRY_KEY])
        file_dialog.setSidebarUrls(file_dialog.sidebarUrls() +
                                   [QUrl.fromLocalFile(os.getcwd())])
        file_dialog.setOptions(QFileDialog.HideNameFilterDetails)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if len(selected_files) == 1:
                file_name = selected_files[0]
                self._parser_manager.parse_file(file_name)
                settings[self.CONFIG_LAST_FILE_KEY] = file_name
        settings[self.CONFIG_FILE_DIALOG_STATE_KEY] = file_dialog.saveState()
        settings[self.CONFIG_FILE_DIALOG_GEOMETRY_KEY] = \
            file_dialog.saveGeometry()

    def terminate_sender(self):
        """Terminate sender, asking the user for permission if still running

        :return: ``True`` if sender was terminated; ``False`` otherwise
        :rtype: bool
        """

        if len(self._sender):
            msg_box = QMessageBox(QMessageBox.Warning, 'Sender is running',
                                  None, QMessageBox.Cancel)
            msg_box.setInformativeText(
                'If you terminate the application now, the data will be '
                'lost. Are you sure you want to quit?')
            terminate_btn = msg_box.addButton('Terminate without sending',
                                              QMessageBox.DestructiveRole)

            if self._sender.paused:
                msg_box.setText('Request queue is paused, but there are still '
                                'some requests that are awaiting to be sent.')
                unpause_btn = msg_box.addButton('Unpause queue',
                                                QMessageBox.AcceptRole)
            else:
                msg_box.setText('There are still some requests that are '
                                'awaiting to be sent.')
                unpause_btn = None

            msg_box.exec()
            clicked_btn = msg_box.clickedButton()
            if clicked_btn == terminate_btn:
                pass
            elif clicked_btn == unpause_btn:
                self._sender.paused = False
                return False
            else:
                # Cancel button
                return False

        self._sender.set_terminated()
        return True

    def terminate_analyzer(self):
        self._analyzer_worker.set_terminated()

    def closeEvent(self, event):
        if self._parser_manager.is_running():
            if not self.terminate_parser():
                event.ignore()
                return
        if not self.terminate_sender():
            event.ignore()
            return
        self.terminate_analyzer()
        self.save_state()

    def save_state(self):
        settings = Settings()
        settings[self.CONFIG_GEOMETRY_KEY] = self.saveGeometry()
        settings[self.CONFIG_STATE_KEY] = self.saveState()
        self.logsDock.save_settings()
