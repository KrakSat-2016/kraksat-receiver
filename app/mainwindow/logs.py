from PyQt5.QtCore import QSortFilterProxyModel, Qt, QRegExp
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QDockWidget, QHeaderView, QAbstractItemView

from app import logger
from app.logstablemodel import LogsTableModel
from app.settings import Settings
from app.ui.ui_logs import Ui_LogsDock


class LogsDock(QDockWidget, Ui_LogsDock):
    CONFIG_LOGS_FILTER_STATE_KEY = 'mainWindow/logs/filterCheckState'

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self._init_table()
        self._init_filter_combo_box()
        self.reset_filter()

    def _init_table(self):
        def on_rows_inserted(index, first, last):
            for i in range(first, last + 1):
                self.table.resizeRowToContents(i)

        source_model = LogsTableModel(self, logger.get_memory_handler())
        model = QSortFilterProxyModel(self)
        model.setSourceModel(source_model)
        model.setFilterKeyColumn(2)  # module column
        self.table.setModel(model)
        model.rowsInserted.connect(on_rows_inserted)

        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setWordWrap(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.table.resizeRowsToContents()

    def _init_filter_combo_box(self):
        model = QStandardItemModel()
        for module in logger.get_modules():
            item = QStandardItem(module)
            item.setData(True, Qt.UserRole)
            model.appendRow(item)

        self.filterComboBox.setModel(model)
        self.filterComboBox.restore_state(Settings().get_bool_list(
                self.CONFIG_LOGS_FILTER_STATE_KEY))

    def reset_filter(self):
        """Get selected modules from logs filter combobox and set them on
        the view filter."""
        auto_checked, *checked = self.filterComboBox.get_check_state()
        modules = logger.get_modules()
        if auto_checked:
            self.table.model().setFilterRegExp('')
        else:
            checked_modules = [QRegExp().escape(modules[i])
                               for i in range(len(modules)) if checked[i]]
            regexp = '^{}$'.format('|'.join(checked_modules))
            if regexp == '':
                # Nothing selected
                self.table.model().setFilterRegExp(QRegExp('$^'))
            else:
                self.table.model().setFilterRegExp(QRegExp(regexp))
        for i in range(3):
            # Resize all columns except Message (which expands automatically)
            self.table.resizeColumnToContents(i)

    def save_settings(self):
        Settings()[self.CONFIG_LOGS_FILTER_STATE_KEY] = \
            list(self.filterComboBox.save_state())
