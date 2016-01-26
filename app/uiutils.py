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
    return max(fm.width(text) for text in texts)
