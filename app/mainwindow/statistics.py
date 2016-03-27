from PyQt5.QtWidgets import QDockWidget

from app import humanize
from app.statistics import QtStatistics
from app.timeutils import natural_timedelta
from app.ui.ui_statistics import Ui_StatisticsDock


class StatisticsDock(QDockWidget, Ui_StatisticsDock):
    def __init__(self, parent, sender, parser_manager):
        """Constructor

        :param QObject parent: dock parent
        :param app.sender.QtSender sender: sender instance
        :param parser_manager: ParserManager instance
        :type parser_manager: app.parser.outputparser.ParserManager
        """
        super().__init__(parent)
        self.setupUi(self)

        self.statistics = QtStatistics(sender, parser_manager, self)
        self.statistics.time_since_start_changed.connect(
                self.update_time_since_start)
        self.statistics.time_since_last_receive_changed.connect(
                self.update_time_since_last_receive)
        self.statistics.messages_parsed_changed.connect(
                self.update_messages_parsed)
        self.statistics.parse_failures_changed.connect(
                self.update_parse_failures)
        self.statistics.requests_sent_changed.connect(
                self.update_requests_sent)
        self.statistics.total_data_received_changed.connect(
                self.update_total_data_received)

    def update_time_since_start(self, timedelta):
        self.timeSinceStartLabel.setText(natural_timedelta(timedelta))

    def update_time_since_last_receive(self, timedelta):
        self.timeSinceLastReceiveLabel.setText(natural_timedelta(timedelta))

    def update_messages_parsed(self, messages_parsed):
        self.messagesParsedLabel.setText(str(messages_parsed))

    def update_parse_failures(self, parse_failures):
        self.parseFailuresLabel.setText(str(parse_failures))

    def update_requests_sent(self, requests_sent):
        self.requestsSentLabel.setText(str(requests_sent))

    def update_total_data_received(self, total_data_received):
        self.totalDataReceivedLabel.setText(
            humanize.format_size(total_data_received))
