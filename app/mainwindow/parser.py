import html
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QLabel

from app.ui.ui_parser import Ui_ParserDock


class ParserDock(QDockWidget, Ui_ParserDock):
    def __init__(self, parent, parser_manager):
        """Constructor

        :param QObject parent: dock parent object
        :param parser_manager: parser manager instance
        :type parser_manager: app.parser.outputparser.ParserManager
        """
        super().__init__(parent)
        self._parser_manager = parser_manager
        self.setupUi(self)

    def create_statusbar_widget(self):
        """Create label for status bar showing current status of the parser

        :return: label widget
        :rtype: QLabel
        """
        parser_label = QLabel()
        parser_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        parser_label.setOpenExternalLinks(True)

        def update_text():
            if self._parser_manager.is_running():
                path = self._parser_manager.path
                dir_path = 'file://' + os.path.dirname(path)
                url_escaped = html.escape(path)
                text = ('Parsing <a href="{}">{}</a>'
                        .format(dir_path, url_escaped))
            else:
                text = (
                    '<span style="color: #f00; font-weight: 700;">'
                    'Parser not running'
                    '</span>'
                )
            parser_label.setText(text)

        update_text()
        self._parser_manager.parser_started.connect(update_text)
        self._parser_manager.parser_terminated.connect(update_text)

        return parser_label
