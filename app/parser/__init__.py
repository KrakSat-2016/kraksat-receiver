class Parser:
    """
    Class for the parsers for the data retrieved from the probe.
    """

    url = None
    """URL of the API endpoint to send returned data to"""

    ids = ()
    """List of the message IDs this parser should handle"""

    def parse(self, id, timestamp, line):
        """Parse a line of output

        :param str id: ID of the message type
        :param datetime.datetime timestamp: message timestamp
        :param str line: output line
        :return: dictionary with the data to send or None, if nothing should
            be sent
        :rtype: dict|None
        """
        pass

    def _get_args(self, line):
        """Utility function to split the line with commas, omitting ID

        :param str line: parsed line
        :return: list of values that were comma-separated without the first
            value (message type ID)
        :rtype: list
        """
        return line.split(',')[1:]


class ParseError(Exception):
    pass
