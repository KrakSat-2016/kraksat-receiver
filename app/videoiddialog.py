import re

from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from app.ui.ui_videoid import Ui_VideoIDDialog

# Extracts video ID from YouTube URL
URL_REGEX = re.compile(
    r'^https?://(?:www\.)?youtu(?:\.be|be\.com)/(?:\S+/)?(?:[^\s/]*'
    r'(?:\?|&)vi?=)?([^#?&]+)')


class VideoIDDialog(QDialog, Ui_VideoIDDialog):
    """Set Video ID dialog"""

    def __init__(self, sender, parent=None):
        """Constructor

        :param app.sender.Sender sender: Sender instance to use
        :param QWidget parent: dialog parent
        """
        super().__init__(parent)
        self._sender = sender

        self.setupUi(self)
        self.submitButton = self.buttonBox.addButton(
            "&Submit", QDialogButtonBox.AcceptRole)

    def accept(self):
        self._send_data()
        self.done(QDialog.Accepted)

    def _send_data(self):
        self._sender.add_request('VideoIDDialog', '/video/', {
            'yt_video_id': self.idLineEdit.text()
        })

    def check_id_contents(self):
        """Check the contents of ID edit and replace URL with ID"""
        try:
            self.idLineEdit.setText(
                self.get_id_from_url(self.idLineEdit.text()))
        except ValueError:
            pass

    @staticmethod
    def get_id_from_url(url):
        """Use regex to retrieve video ID from given YouTube URL

        :param str url: YouTube video URL
            (e.g. https://www.youtube.com/watch?v=X_hMZYDMps4)
        :return: YouTube video ID
        :rtype: str
        :raises ValueError: if given url is not a YouTube video URL
        """
        try:
            return URL_REGEX.match(url).group(1)
        except (AttributeError, IndexError):
            raise ValueError('Invalid YouTube URL')
