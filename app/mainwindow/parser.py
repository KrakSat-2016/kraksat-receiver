import html
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class QtParser:
    @staticmethod
    def create_statusbar_widget(parser_manager):
        """Create label for status bar showing current status of the parser

        :param parser_manager: parser manager instance
        :type parser_manager: app.parser.outputparser.ParserManager
        :return: label widget
        :rtype: QLabel
        """
        parser_label = QLabel()
        parser_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        parser_label.setOpenExternalLinks(True)

        def update_text():
            if parser_manager.is_running():
                path = parser_manager.path
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
        parser_manager.parser_started.connect(update_text)
        parser_manager.parser_terminated.connect(update_text)

        return parser_label
