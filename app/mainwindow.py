from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from app.settings import get_settings, settings_get_bool_list
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
        settings = get_settings()
        self.restoreGeometry(settings.value(self.CONFIG_GEOMETRY_KEY))
        self.restoreState(settings.value(self.CONFIG_STATE_KEY))

        docks = (self.logsDock, self.queueDock, self.statisticsDock,
                 self.cameraDock)
        for dock in docks:
            self.menuView.addAction(dock.toggleViewAction())

        self._init_logs_filter_combo_box(settings)

    def _init_logs_filter_combo_box(self, settings):
        model = QStandardItemModel()

        item1 = QStandardItem()
        item1.setText("system")
        item1.setData(False, Qt.UserRole)
        item2 = QStandardItem("ui")
        item2.setData(False, Qt.UserRole)
        item3 = QStandardItem("parser")
        item3.setData(False, Qt.UserRole)

        model.insertRow(0, item1)
        model.insertRow(1, item2)
        model.insertRow(2, item3)

        self.logsFilterComboBox.setModel(model)
        self.logsFilterComboBox.popup_hidden.connect(self.reset_logs_filter)
        self.logsFilterComboBox.restore_state(settings_get_bool_list(
                settings, self.CONFIG_LOGS_FILTER_STATE_KEY))

    def reset_logs_filter(self):
        pass

    def show_about(self):
        QMessageBox().about(self, 'About KrakSat 2016 Ground Station Software',
                            ABOUT_HTML)

    def closeEvent(self, QCloseEvent):
        settings = get_settings()
        settings.setValue(self.CONFIG_GEOMETRY_KEY, self.saveGeometry())
        settings.setValue(self.CONFIG_STATE_KEY, self.saveState())
        settings.setValue(self.CONFIG_LOGS_FILTER_STATE_KEY,
                          list(self.logsFilterComboBox.save_state()))
