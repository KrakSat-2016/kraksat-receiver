import logging

from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QUrl
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QHeaderView, QAbstractItemView, QLabel
)

from app import logger
from app.logstablemodel import LogsTableModel
from app.settings import Settings
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
    CONFIG_LOGS_FILTER_STATE_KEY = 'mainWindow/logs/filterCheckState'
    CONFIG_QUEUE_FILTER_STATE_KEY = 'mainWindow/queue/filterCheckState'

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.webview_go_home()
        settings = Settings()
        self.restoreGeometry(settings.value(self.CONFIG_GEOMETRY_KEY))
        self.restoreState(settings.value(self.CONFIG_STATE_KEY))

        docks = (self.logsDock, self.queueDock, self.statisticsDock,
                 self.cameraDock)
        for dock in docks:
            self.menuView.addAction(dock.toggleViewAction())

        self._init_statusbar()
        self._init_logs(settings)
        logging.getLogger('mainwindow').info("Main Window initialized")

    def _init_statusbar(self):
        self.queue_status_label = QLabel()
        self.statusBar().addPermanentWidget(self.queue_status_label)
        self.update_queue_status_label()

    def update_queue_status_label(self):
        # todo change it to something smarter when there's a queue implemented
        count = 0
        self.queue_status_label.setText("Processing {} requests".format(count))

    def _init_logs(self, settings):
        self._init_logs_view()
        self._init_logs_filter_combo_box(settings)
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

    def _init_logs_filter_combo_box(self, settings):
        model = QStandardItemModel()
        for module in logger.get_modules():
            item = QStandardItem(module)
            item.setData(True, Qt.UserRole)
            model.appendRow(item)

        self.logsFilterComboBox.setModel(model)
        self.logsFilterComboBox.popup_hidden.connect(self.reset_logs_filter)
        self.logsFilterComboBox.restore_state(settings.get_bool_list(
                self.CONFIG_LOGS_FILTER_STATE_KEY))

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
            regexp = '|'.join(checked_modules)
            if regexp == '':
                # Nothing selected
                self.logsView.model().setFilterRegExp(QRegExp('$^'))
            else:
                self.logsView.model().setFilterRegExp(QRegExp(regexp))
        for i in range(3):
            # Resize all columns except Message (which expands automatically)
            self.logsView.resizeColumnToContents(i)

    def show_about(self):
        QMessageBox().about(self, 'About KrakSat 2016 Ground Station Software',
                            ABOUT_HTML)

    def webview_go_home(self):  # you are drunk
        # todo set to our equivalent of live.techswarm.org as soon as it runs
        self.webView.setUrl(QUrl('http://cansat.kraksat.pl'))

    def closeEvent(self, QCloseEvent):
        settings = Settings()
        settings.setValue(self.CONFIG_GEOMETRY_KEY, self.saveGeometry())
        settings.setValue(self.CONFIG_STATE_KEY, self.saveState())
        settings.setValue(self.CONFIG_LOGS_FILTER_STATE_KEY,
                          list(self.logsFilterComboBox.save_state()))
