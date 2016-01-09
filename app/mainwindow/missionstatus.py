from datetime import datetime

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDockWidget
from dateutil.tz import tzutc

from app import api, timeutils
from app.ui.ui_missionstatus import Ui_MissionStatusDock


class MissionStatusDock(QDockWidget, Ui_MissionStatusDock):
    MISSION_STATES = (
        ('', 'None'),
        ('launch_preparation', 'Launch preparation'),
        ('countdown', 'Countdown'),
        ('launch', 'Launch'),
        ('descent', 'Descent'),
        ('ground_operations', 'Ground operations'),
        ('mission_complete', 'Mission complete')
    )

    data_submitted = pyqtSignal()
    """Used to refresh the form after submit"""

    def __init__(self, parent, sender):
        """Constructor

        :param QWidget parent: dock parent
        :param app.sender.Sender sender: Sender instance to use
        """
        super().__init__(parent)
        self._sender = sender

        # Timestamp of the last change to calculate mission time
        self.last_change = None
        self.last_time = None

        self.data_submitted.connect(self.refresh)
        self.setupUi(self)
        self._init_state_combo_box()
        self.refresh()

    def _init_state_combo_box(self):
        for item, label in self.MISSION_STATES:
            self.stateComboBox.addItem(label, item)

    def refresh(self):
        """Request /status/ and refresh the form fields when response is got"""
        self.set_ui_locked(True)
        api.APIWorker(self._sender.api.get_status, self,
                      self._set_mission_status, self.set_ui_locked)

    def _set_mission_status(self, timestamp, state, mission_time,
                            cansat_online):
        """Set data in the form fields

        :param datetime.datetime timestamp: timestamp of the last change
        :param str state: current mission phase
        :param float mission_time: current mission time
        :param bool cansat_online: whether or not the CanSat is connected
        """
        self.last_change = timestamp.astimezone(tzutc()).replace(tzinfo=None)
        self.last_time = mission_time

        self.lastChangeLabel.setText(timestamp.strftime(timeutils.DT_FORMAT))
        for i in range(len(self.MISSION_STATES)):
            if state == self.MISSION_STATES[i][0]:
                self.stateComboBox.setCurrentIndex(i)
                break
        if mission_time is None:
            self.missionTimeSpinBox.setValue(self.missionTimeSpinBox.minimum())
        else:
            self.missionTimeSpinBox.setValue(mission_time)
        self.canSatOnlineCheckBox.setChecked(cansat_online)

    def submit(self):
        """Send the data entered into the form fields to the server"""
        self.set_ui_locked(True)

        # Get mission time
        now = datetime.utcnow()
        if self.missionTimeCheckBox.isChecked():
            # Take user input as new mission time
            mission_time = self.missionTimeSpinBox.value()
            if mission_time == self.missionTimeSpinBox.minimum():
                # Special "None" value
                mission_time = None
        else:
            # Calculate mission time
            mission_time = get_current_mission_time(self.last_change, now,
                                                    self.last_time)

        self._sender.add_request('missionstatus', '/status/', {
            'timestamp': api.encode_datetime(now),
            'phase': self.stateComboBox.currentData(),
            'mission_time': mission_time,
            'cansat_online': self.canSatOnlineCheckBox.isChecked()
        }, append_timestamp=False, callback=self.data_submitted.emit)

    def set_ui_locked(self, locked=False):
        """Enable or disable dock form fields and buttons

        :param bool locked: ``True`` if the fields should be disabled;
            ``False`` otherwise
        """
        widgets = (
            self.stateComboBox, self.missionTimeCheckBox,
            self.missionTimeFrame, self.canSatOnlineCheckBox,
            self.refreshButton, self.submitButton
        )
        for widget in widgets:
            widget.setEnabled(not locked)
        if not locked:
            self.missionTimeFrame.setEnabled(
                    self.missionTimeCheckBox.isChecked())

    def set_none_mission_time(self):
        """Set mission time spin box value to 'None'"""
        spin_box = self.missionTimeSpinBox
        spin_box.setValue(spin_box.minimum())


def get_current_mission_time(last_change, now, last_time):
    """Calculate current mission time using the old value

    :param datetime|None last_change: timestamp of the last mission time change
        (the function assumes this parameter is naive datetime object)
    :param float|None last_time: "current" mission time at ``last_change``
    :param datetime now: the result of ``datetime.utcnow()``
    :return: Calculated mission time or ``None`` if any of the parameters
        is ``None``
    :rtype: float|None
    """
    if last_change is None or last_time is None:
        return None

    delta = now - last_change
    delta.total_seconds()
    return last_time + delta.total_seconds()
