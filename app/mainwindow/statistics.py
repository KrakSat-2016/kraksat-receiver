from PyQt5.QtWidgets import QDockWidget

from app.statistics import QtStatistics
from app.timeutils import natural_timedelta
from app.ui.ui_statistics import Ui_StatisticsDock


class StatisticsDock(QDockWidget, Ui_StatisticsDock):
    def __init__(self, parent, sender):
        """Constructor

        :param QObject parent: dock parent
        :param app.sender.QtSender sender: sender instance
        """
        super().__init__(parent)
        self.setupUi(self)

        self.statistics = QtStatistics(sender, self)
        self.statistics.time_since_start_changed.connect(
                self.update_time_since_start)
        self.statistics.time_since_last_receive_changed.connect(
                self.update_time_since_last_receive)
        self.statistics.requests_sent_changed.connect(
                self.update_requests_sent)

    def update_time_since_start(self, timedelta):
        self.timeSinceStartLabel.setText(natural_timedelta(timedelta))

    def update_time_since_last_receive(self, timedelta):
        self.timeSinceLastReceiveLabel.setText(natural_timedelta(timedelta))

    def update_requests_sent(self, requests_sent):
        self.requestsSentLabel.setText(str(requests_sent))
