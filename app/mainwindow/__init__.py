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
from app.sender.sendererrorcatcher import QtSenderErrorCatcher
from app.settings import Settings
from app.ui.ui_main import Ui_MainWindow

with open(os.path.join(os.path.dirname(__file__), 'about.html')) as f:
    ABOUT_HTML = f.read().strip()


class MainWindow(QMainWindow, Ui_MainWindow):
    CONFIG_GEOMETRY_KEY = 'mainWindow/geometry'
    CONFIG_STATE_KEY = 'mainWindow/state'
    CONFIG_LAST_FILE_KEY = 'mainWindow/lastFile'
    CONFIG_FILE_DIALOG_STATE_KEY = 'mainWindow/fileDialogState'

    logger = logging.getLogger('MainWindow')

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
        self.sender_error_catcher = QtSenderErrorCatcher(self, sender)

        self.webview_go_home()
        self._init_docks()
        self._init_actions()
        self._init_toolbars()
        settings = Settings()
        self.restoreGeometry(settings[self.CONFIG_GEOMETRY_KEY])
        self.restoreState(settings[self.CONFIG_STATE_KEY])
        self._init_statusbar()

        self.logger.info("Main Window initialized")

    def _init_docks(self):
        self.logsDock = LogsDock(self)
        self.queueDock = QueueDock(self, self._sender)
        self.statisticsDock = StatisticsDock(self, self._sender,
                                             self._parser_manager)
        self.missionStatusDock = MissionStatusDock(self, self._sender)
        docks = {
            Qt.LeftDockWidgetArea: (
                self.statisticsDock,
                self.queueDock,
                self.missionStatusDock,
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

    def show_about(self):
        QMessageBox().about(self, 'About KrakSat 2016 Ground Station Software',
                            ABOUT_HTML)

    def show_about_qt(self):
        QApplication.aboutQt()

    def webview_go_home(self):  # you are drunk
        # todo set to our equivalent of live.techswarm.org as soon as it runs
        self.webView.setUrl(QUrl('http://cansat.kraksat.pl'))

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

    def choose_parser_file(self):
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
        file_dialog.selectFile(settings.value(self.CONFIG_LAST_FILE_KEY,
                                              os.getcwd()))
        if self.CONFIG_FILE_DIALOG_STATE_KEY in settings:
            file_dialog.restoreState(
                settings[self.CONFIG_FILE_DIALOG_STATE_KEY])
        file_dialog.setOptions(QFileDialog.HideNameFilterDetails)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if len(selected_files) == 1:
                file_name = selected_files[0]
                self._parser_manager.parse_file(file_name)
                settings[self.CONFIG_LAST_FILE_KEY] = file_name
        settings[self.CONFIG_FILE_DIALOG_STATE_KEY] = file_dialog.saveState()

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

    def closeEvent(self, event):
        if self._parser_manager.is_running():
            if not self.terminate_parser():
                event.ignore()
                return
        if not self.terminate_sender():
            event.ignore()
            return
        self.save_state()

    def save_state(self):
        settings = Settings()
        settings[self.CONFIG_GEOMETRY_KEY] = self.saveGeometry()
        settings[self.CONFIG_STATE_KEY] = self.saveState()
        self.logsDock.save_settings()
