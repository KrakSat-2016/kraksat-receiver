import logging
import os

from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QUrl
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QHeaderView, QAbstractItemView, QLabel,
    QStylePainter
)

from app import logger
from app.gsinfodialog import GSInfoDialog
from app.logstablemodel import LogsTableModel
from app.queuetablemodel import QueueTableModel
from app.settings import Settings
from app.ui.ui_main import Ui_MainWindow

with open(os.path.join(os.path.dirname(__file__), 'about.html')) as f:
    ABOUT_HTML = f.read().strip()


class MainWindow(QMainWindow, Ui_MainWindow):
    CONFIG_GEOMETRY_KEY = 'mainWindow/geometry'
    CONFIG_STATE_KEY = 'mainWindow/state'
    CONFIG_LOGS_FILTER_STATE_KEY = 'mainWindow/logs/filterCheckState'
    CONFIG_QUEUE_FILTER_STATE_KEY = 'mainWindow/queue/filterCheckState'

    def __init__(self, sender):
        """Constructor

        :param app.sender.QtSender sender: QtSender instance to use with
            QueueTableModel
        """
        super(MainWindow, self).__init__()
        self._sender = sender

        self.setupUi(self)
        self.webview_go_home()
        settings = Settings()
        self.restoreGeometry(settings[self.CONFIG_GEOMETRY_KEY])
        self.restoreState(settings[self.CONFIG_STATE_KEY])

        docks = (self.logsDock, self.queueDock, self.statisticsDock,
                 self.missionStatusDock, self.cameraDock)
        for dock in docks:
            self.menuView.addAction(dock.toggleViewAction())

        self._init_logs()
        self._init_queue()
        self._init_statusbar()
        logging.getLogger('mainwindow').info("Main Window initialized")

    def _init_statusbar(self):
        self.queue_status_label = QLabel()
        self.statusBar().addPermanentWidget(self.queue_status_label)
        self.update_queue_status_label()
        queue_model = self.queueView.model().sourceModel()
        queue_model.rowsInserted.connect(self.update_queue_status_label)
        queue_model.rowsRemoved.connect(self.update_queue_status_label)

    def update_queue_status_label(self):
        """Update "Processing ... requests" label text on status bar"""
        count = self.queueView.model().sourceModel().rowCount()
        self.queue_status_label.setText("Processing {} requests".format(count))

    def _init_logs(self):
        self._init_logs_view()
        self._init_logs_filter_combo_box()
        self.reset_logs_filter()

    def _init_logs_view(self):
        def on_rows_inserted(index, first, last):
            for i in range(first, last + 1):
                self.logsView.resizeRowToContents(i)

        source_model = LogsTableModel(self, logger.get_memory_handler())
        model = QSortFilterProxyModel(self)
        model.setSourceModel(source_model)
        model.setFilterKeyColumn(2)  # module column
        self.logsView.setModel(model)
        model.rowsInserted.connect(on_rows_inserted)

        self.logsView.verticalHeader().hide()
        self.logsView.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeToContents)
        self.logsView.horizontalHeader().setStretchLastSection(True)

        self.logsView.setWordWrap(False)
        self.logsView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.logsView.resizeRowsToContents()

    def _init_logs_filter_combo_box(self):
        model = QStandardItemModel()
        for module in logger.get_modules():
            item = QStandardItem(module)
            item.setData(True, Qt.UserRole)
            model.appendRow(item)

        self.logsFilterComboBox.setModel(model)
        self.logsFilterComboBox.popup_hidden.connect(self.reset_logs_filter)
        self.logsFilterComboBox.restore_state(Settings().get_bool_list(
                self.CONFIG_LOGS_FILTER_STATE_KEY))

    def _init_queue(self):
        self._init_queue_view()
        # todo init queue filter combo box

    def _init_queue_view(self):
        def on_rows_inserted(index, first, last):
            for i in range(first, last + 1):
                self.queueView.resizeRowToContents(i)

        source_model = QueueTableModel(self._sender, self)
        model = QSortFilterProxyModel(self)
        model.setSourceModel(source_model)
        model.setFilterKeyColumn(1)  # module column
        self.queueView.setModel(model)
        model.rowsInserted.connect(on_rows_inserted)

        self.queueView.verticalHeader().hide()
        self.queueView.horizontalHeader().setSectionResizeMode(
                QHeaderView.Fixed)
        # Resize columns basing on maximum contents widths
        fm = QStylePainter(self.queueView).fontMetrics()
        # We don't expect the number of requests to exceed 10M
        self.queueView.horizontalHeader().resizeSection(
                0, fm.width('0000000') + 6)
        # todo set to the longest module name width
        self.queueView.horizontalHeader().resizeSection(
                1, fm.width('0000000') + 6)
        self.queueView.horizontalHeader().setStretchLastSection(True)

        self.queueView.setWordWrap(False)
        self.queueView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.queueView.resizeRowsToContents()

    def reset_logs_filter(self):
        """Get selected modules from logs filter combobox and set them on
        the view filter."""
        auto_checked, *checked = self.logsFilterComboBox.get_check_state()
        modules = logger.get_modules()
        if auto_checked:
            self.logsView.model().setFilterRegExp('')
        else:
            checked_modules = [QRegExp().escape(modules[i])
                               for i in range(len(modules)) if checked[i]]
            regexp = '^{}$'.format('|'.join(checked_modules))
            if regexp == '':
                # Nothing selected
                self.logsView.model().setFilterRegExp(QRegExp('$^'))
            else:
                self.logsView.model().setFilterRegExp(QRegExp(regexp))
        for i in range(3):
            # Resize all columns except Message (which expands automatically)
            self.logsView.resizeColumnToContents(i)

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
        settings[self.CONFIG_LOGS_FILTER_STATE_KEY] = \
            list(self.logsFilterComboBox.save_state())
