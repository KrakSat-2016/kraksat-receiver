from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QDockWidget

from app.ui.ui_camera import Ui_CameraDock


class CameraDock(QDockWidget, Ui_CameraDock):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.camera = None

        self.viewfinder = QCameraViewfinder(self)
        self.verticalLayout.addWidget(self.viewfinder)
        self.viewfinder.show()

    def set_up_camera(self, camera):
        if self.camera is not None:
            self.camera.setViewfinder(None)
            self.camera.stop()

        self.camera = camera

        if camera is not None:
            self.camera.setViewfinder(self.viewfinder)
            self.camera.setCaptureMode(QCamera.CaptureVideo)
            self.imageCapture = QCameraImageCapture(self.camera)

            self.camera.start()

    def change_camera(self, camera_info):
        if camera_info is None:
            cam = None
        else:
            cam = QCamera(self.cameraComboBox.get_current_camera_info())
        self.set_up_camera(cam)
