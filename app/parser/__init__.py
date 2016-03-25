import collections


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

    id = None
    """Single message ID this parser handles, or list of the message IDs"""

    serializer = None
    """Serializer class to use to parse the data, or dictionary containing
    (message ID -> serializer class) mappings"""

    def __init__(self):
        # Create serializer instance(s)
        if isinstance(self.serializer, dict):
            self._serializers = {}
            for key, value in self.serializer.items():
                self._serializers[key] = value()
        else:
            self.serializer = self.serializer()

    def can_parse(self, line):
        """Check if given file can be parsed by current Parser

        Default implementation iterates over the IDs specified in `self.id`
        and returns one if found at the beginning of provided line.

        :param str line: line to be parsed
        :return: message ID if given line can be parsed by current Parser;
            `False` otherwise
        :rtype: str|bool
        """
        if isinstance(self.id, collections.Iterable):
            for msg_id in self.id:
                if line.startswith(msg_id):
                    return msg_id
        elif isinstance(self.id, str):
            if line.startswith(self.id):
                return self.id
        return False

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
        if isinstance(self.serializer, dict):
            if line.id in self._serializers:
                return self._serializers[line.id].parse(line.content).as_dict()
            raise NotImplementedError
        return self.serializer.parse(line.content).as_dict()


class ParseError(Exception):
    def __init__(self, message, parser_name=None):
        super().__init__(message)
        self.parser_name = parser_name
