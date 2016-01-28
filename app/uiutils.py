from PyQt5.QtCore import QTimer

# Default padding for table cells (for both sides, i.e. left *and* right, or
# top and bottom, for single side divide the values by 2)
TABLE_WIDTH_PADDING = 8
TABLE_HEIGHT_PADDING = 4


def get_max_text_width(fm, texts):
    """Get maximum width of texts from given list

    :param QtGui.QFontMetrics fm: FontMetrics instance
    :param iterable texts: list of texts
    :return: maximum text width
    :rtype: int
    """
    return max(map(fm.width, texts))


def setup_autoscroll(view):
    """Setup smart autoscroll for given view

    "Smart" autoscroll means that the view will be scrolled to the bottom if
    and only if the view was already at the bottom before adding new items.

    :param view: view to setup the autoscroll in
    """
    def rows_before_insert():
        scroll_bar = view.verticalScrollBar()
        view.setProperty('autoscroll_enabled',
                         scroll_bar.value() == scroll_bar.maximum())

    def rows_inserted():
        if view.property('autoscroll_enabled'):
            view.scrollToBottom()

    model = view.model()
    model.rowsAboutToBeInserted.connect(rows_before_insert)
    # Calling rows_inserted immediately and after 0ms timer to avoid problems
    # when adding a lot of rows at once
    model.rowsInserted.connect(rows_inserted)
    model.rowsInserted.connect(lambda: QTimer().singleShot(0, rows_inserted))
