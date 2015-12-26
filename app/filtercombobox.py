from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QCheckBox

from app.checkcombobox import CheckComboBox, CheckComboBoxDelegate


class FilterComboBoxDelegate(CheckComboBoxDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        # List of bools that stores whether items were checked when user
        # selects "All" item, so it can be restored when "All" is unchecked
        self.checked_state = None

    def createEditor(self, parent, option, index):
        editor = QCheckBox(parent)
        if index.row() == 0:
            editor.stateChanged.connect(self.all_item_state_changed)
        else:
            editor.stateChanged.connect(
                    lambda state: self.normal_item_state_changed(index, state))
        return editor

    def all_item_state_changed(self, state):
        model = self.parent().model()
        count = model.rowCount() - 1

        # When user checks the "All" checkbox, we are saving the states of
        # other checkboxes so we can restore them when user un-checks "All"
        if state == Qt.Checked:
            checked_state = []
            for i in range(count):
                index = model.index(i + 1, 0)
                checked_state.append(model.data(index, Qt.UserRole))
                model.setData(index, True, Qt.UserRole)

            if not all(checked_state):
                # If we didn't get all Trues
                self.checked_state = checked_state
        else:
            for i in range(count):
                index = model.index(i + 1, 0)
                if self.checked_state:
                    model.setData(index, self.checked_state[i], Qt.UserRole)
                else:
                    model.setData(index, False, Qt.UserRole)

    def normal_item_state_changed(self, index, state):
        model = self.parent().model()
        count = model.rowCount() - 1

        all_checked = True
        for i in range(count):
            cur_index = model.index(i + 1, 0)
            if index == cur_index:
                # We are at editor's item
                checked = state == Qt.Checked
            else:
                checked = model.data(cur_index, Qt.UserRole)

            if not checked:
                all_checked = False
                break

        all_checkbox_index = model.index(0, 0)
        if model.data(all_checkbox_index, Qt.UserRole) != all_checked:
            # Only if "All" checked state changed
            model.setData(all_checkbox_index, all_checked, Qt.UserRole)
            # We should ignore saved checkbox states
            self.checked_state = None


class FilterComboBox(CheckComboBox):
    """
    CheckComboBox (ComboBox that allows to select multiple values) that is
    intended to allow to select groups for filtering.

    Basically, what the FilterComboBox does is it appends "Select all" item
    at the top and provides convenient methods (`save_state` and
    `restore_state`) for saving and restoring current state of a ComboBox
    to/from a list of booleans. Also, it automatically generates display text
    by listing selected values.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        delegate = FilterComboBoxDelegate(self)
        delegate.closeEditor.connect(self.update_display_text)
        self.setItemDelegate(delegate)

    def setModel(self, model):
        """Add "All" item at the top and set new model."""
        all_item = QStandardItem("All")
        all_item.setData(True, Qt.UserRole)
        model.insertRow(0, all_item)
        super().setModel(model)
        self.update_display_text()

    def update_display_text(self):
        """Update display_text value for the ComboBox using selected values."""
        model = self.model()
        if model.data(model.index(0, 0), Qt.UserRole):
            self.display_text = "All"
        else:
            l = []
            for i in range(1, model.rowCount()):
                index = model.index(i, 0)
                checked = model.data(index, Qt.UserRole)
                if checked:
                    l.append(model.data(index, Qt.DisplayRole))
            self.display_text = ", ".join(l)
            if not self.display_text:
                self.display_text = "None"

    def save_state(self):
        """Save ComboBox state as a list of booleans.

        :return: List of ComboBox "checked" values (for all items except "All")
            with checked_state from FilterComboBoxDelegate appended, if not
            None. The return value is intended to be used with restore_state
            method.
        :rtype: list[bool]
        """
        result = list(self.get_check_state())[1:]
        checked_state = self.itemDelegate().checked_state
        if checked_state:
            result += checked_state
        return result

    def restore_state(self, state):
        """Restore ComboBox state.

        :param list[bool] state: return value from save_state function.
        """
        row_count = self.model().rowCount() - 1  # We don't count "All" item
        if len(state) != row_count and len(state) != row_count * 2:
            # Probably corrupted settings, we store either checked values for
            # all items except "All", or checked values and checked_state for
            # item delegate
            return

        all_checked = all(state[:row_count])
        self.set_check_state([all_checked] + state[:row_count])
        if len(state) == row_count * 2:
            self.itemDelegate().checked_state = state[row_count:]
        self.update_display_text()
