import re

from app.parser import Parser
from app.parser.serializer import fields, Serializer


class KundtSerializer(Serializer):
    frequency = fields.FrequencyField()
    amplitude = fields.HexIntegerField()

    def get_data(self, line_content):
        return line_content.split(self.separator)


class KundtParser(Parser):
    """Parser for the output from Kundt's tube

    The line of data is simply a pair of frequency, amplitude hex values
    without any additional identifying string at the beginning.
    """

    url = '/kundt/'
    id = 'KUNDT'
    serializer = KundtSerializer

    # Regex that identifies Kundt message
    LINE_REGEX = re.compile(r'^\d+,\d+$')

    def can_parse(self, line):
        if self.LINE_REGEX.match(line):
            return 'KUNDT'
        return False
