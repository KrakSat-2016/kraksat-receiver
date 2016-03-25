from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QItemDelegate, QApplication, QStyleOptionButton, QStyle,
    QComboBox, QAbstractItemView, QStylePainter, QStyleOptionComboBox,
    QCheckBox
)


class CheckComboBoxDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        value = index.data(Qt.UserRole)
        text = index.data(Qt.DisplayRole)

        opt = QStyleOptionButton()
        opt.state |= QStyle.State_On if value else QStyle.State_Off
        opt.text = text
        opt.rect = option.rect

        QApplication.style().drawControl(QStyle.CE_CheckBox, opt, painter)

    def createEditor(self, parent, option, index):
        return QCheckBox(parent)

    def setEditorData(self, editor, index):
        editor.setText(index.data(Qt.DisplayRole))
        editor.setChecked(index.data(Qt.UserRole))

    def setModelData(self, editor, model, index):
        data = {
            Qt.DisplayRole: editor.text(),
            Qt.UserRole: editor.isChecked()
        }
        model.setItemData(index, data)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        return self.parent().sizeHint()


class CheckComboBox(QComboBox):
    """
    ComboBox that allows the user to select multiple values by placing
    CheckBoxes next to items.

    Note that this requires model items to have data with role `Qt.UserRole`
    set to `True` or `False`, which means they are going to be checked or not,
    respectively.

    For setting and getting "checked" values for all items at once,
    `set_check_state` and `get_check_state` methods are available.
    """
    popup_hidden = pyqtSignal()
    """Signal emitted when ComboBox popup is being hidden."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.display_text = ''

        self.view().setItemDelegate(CheckComboBoxDelegate(self))
        self.view().setEditTriggers(QAbstractItemView.CurrentChanged)
        self.view().viewport().installEventFilter(self)
        self.view().setAlternatingRowColors(True)

    def hidePopup(self):
        super().hidePopup()
        self.popup_hidden.emit()

    def eventFilter(self, obj, event):
        # Don't close items view after we release the mouse button
        if (event.type() == QEvent.MouseButtonRelease and
                obj == self.view().viewport()):
            return True
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))

        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        opt.currentText = self.display_text
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)

    def set_check_state(self, checked_list):
        """Utility function to set "checked" values using a list of bools.

        :param iterable checked_list: list of booleans to set "checked" values
            from, i.e. checked_list[i] == True if i-th item is intended to
            be checked
        :raise ValueError: if length of checked_list does not equal the number
            of rows in ComboBox model
        """
        model = self.model()
        if not checked_list or len(checked_list) != model.rowCount():
            raise ValueError('Length of checked_list provided does not equal '
                             'the number of rows in the model')

        for i in range(model.rowCount()):
            index = model.index(i, 0)
            model.setData(index, checked_list[i], Qt.UserRole)

    def get_check_state(self):
        """Yield ComboBox "checked" values."""
        model = self.model()
        for i in range(model.rowCount()):
            yield model.data(model.index(i, 0), Qt.UserRole)
