import collections


class OutputLine:
    __slots__ = ['id', 'parse_timestamp', 'last_timestamp', 'content']

    def __init__(self, id, parse_timestamp, last_timestamp, content):
        """Constructor

        :param str id: ID of the message type
        :param datetime.datetime parse_timestamp: timestamp of message parse
        :param datetime.datetime last_timestamp: last value for 'timestamp' key
        :param str content: output line
        """
        self.id = id
        self.parse_timestamp = parse_timestamp
        self.last_timestamp = last_timestamp
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

    def parse(self, line, probe_start_time, collector=None):
        """Parse a line of output

        The method tries to use defined serializers by default, raising
        :py:class:`NotImplementedError` if no serializer is available for given
        message ID. Subclasses should override this method for custom behavior.

        :param OutputLine line: output line (as an instance of OutputLine
            class)
        :param datetime.datetime probe_start_time: datetime of probe software
            start; used to create values in TimestampFields
        :param analyzer.collector.Collector collector: Collector instance to
            pass the parsed data to
        :return: dictionary with the data to send or None, if nothing should
            be sent
        :rtype: dict|None
        """
        if isinstance(self.serializer, dict):
            if line.id in self._serializers:
                serializer = self._serializers[line.id]
            else:
                raise NotImplementedError
        else:
            serializer = self.serializer

        data = serializer.parse(line.content, probe_start_time)
        data_dict = data.as_dict()
        timestamp = (data_dict['timestamp'] if 'timestamp' in data_dict
                     else line.last_timestamp)

        # Add data to the collector
        collector_data = serializer.get_collector_data(data)
        if collector and collector_data:
            for key, value in collector_data.items():
                collector.add_value(timestamp, key, value)

        return data_dict


class ParseError(Exception):
    def __init__(self, message, parser_name=None):
        super().__init__(message)
        self.parser_name = parser_name
