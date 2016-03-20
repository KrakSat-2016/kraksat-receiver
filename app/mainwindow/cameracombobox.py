from PyQt5.QtCore import Qt, QAbstractListModel, pyqtSignal
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import QComboBox


CAMERAS_INDEX_OFFSET = 1


class CameraComboBoxModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cameras = QCameraInfo.availableCameras()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.cameras) + 1

    def data(self, index, role=None):
        row = index.row()

        if row == 0:
            if role == Qt.DisplayRole:
                return 'None'
        cam = self.get_camera_for_row(row)

        if role == Qt.DisplayRole:
            return '{} ({})'.format(cam.description(), cam.deviceName())

    def get_camera_for_row(self, row):
        return self.cameras[row - CAMERAS_INDEX_OFFSET]


class CameraComboBox(QComboBox):
    camera_selected = pyqtSignal('QCameraInfo')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_camera_info = None
        self.refresh()

    def refresh(self):
        self.setModel(CameraComboBoxModel(self))

        for i, camera_info in enumerate(self.model().cameras,
                                        CAMERAS_INDEX_OFFSET):
            # Set previously set camera
            if camera_info == self.current_camera_info:
                self.setCurrentIndex(i)
                break
        else:
            # If previously set camera is not available now (or if there was
            # no selection), set None
            self.setCurrentIndex(0)

    def item_selected(self, index):
        # fixme not called when currently selected item is removed after
        # refresh and user clicks outside the combobox afterwards (i.e. does
        # not select anything, but the real selection was changed)

        if index == -1 or index == 0:
            # No selection or "None" item
            camera_info = None
        else:
            camera_info = self.model().get_camera_for_row(index)

        if self.current_camera_info != camera_info:
            self.current_camera_info = camera_info
            self.camera_selected.emit(self.current_camera_info)

    def get_current_camera_info(self):
        """Get QCameraInfo of the selected item, or None if none is selected

        :rtype: QCameraInfo|None
        """
        return self.current_camera_info

    def showPopup(self):
        self.refresh()
        super().showPopup()
