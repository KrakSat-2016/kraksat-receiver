import html

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QToolTip


class AutoToolTipDelegate(QStyledItemDelegate):
    """
    Item delegate that automatically displays a ToolTip for an item if it is
    too long to be displayed.
    """

    def helpEvent(self, event, view, option, index):
        if not (event and view):
            return False

        if event.type() == QEvent.ToolTip and not index.data(Qt.ToolTipRole):
            rect = view.visualRect(index)
            size = self.sizeHint(option, index)

            # Compare actual cell width and text width
            if rect.width() < size.width():
                text = index.data(Qt.DisplayRole)
                QToolTip.showText(event.globalPos(),
                                  '<div>{}</div>'.format(html.escape(text)),
                                  view)
                return True

            if not super().helpEvent(event, view, option, index):
                QToolTip.hideText()
            return True

        return super().helpEvent(event, view, option, index)
