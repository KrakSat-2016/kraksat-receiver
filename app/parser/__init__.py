class OutputLine:
    def __init__(self, id, timestamp, content):
        """Constructor

        :param str id: ID of the message type
        :param datetime.datetime timestamp: message timestamp
        :param str content: output line
        """
        self.id = id
        self.timestamp = timestamp
        self.content = content


class Parser:
    """
    Class for the parsers for the data retrieved from the probe.
    """

    url = None
    """URL of the API endpoint to send returned data to"""

    ids = ()
    """List of the message IDs this parser should handle"""

    serializers = {}
    """Dictionary containing (message ID -> serializer class) mappings for
    easy data parsing"""

    def __init__(self):
        self._serializers = {}
        for key, value in self.serializers.items():
            self._serializers[key] = value()

    def parse(self, line):
        """Parse a line of output

        The method tries to use defined serializers by default, raising
        :py:class:`NotImplementedError` if no serializer is available for given
        message ID. Subclasses should override this method for custom behavior.

        :param OutputLine line: output line (as an instance of OutputLine
            class)
        :return: dictionary with the data to send or None, if nothing should
            be sent
        :rtype: dict|None
        """
        if line.id in self._serializers:
            return self._serializers[line.id].parse(line.content).as_dict()
        raise NotImplementedError

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
