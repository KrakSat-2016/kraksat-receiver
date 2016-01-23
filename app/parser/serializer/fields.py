from app.parser import ParseError


class ValidationError(ParseError):
    """
    Exception raised in case of errors during field validation

    Except the message, one can also set ``field`` attribute to store the name
    of field this error occurred on as well as ``field_id`` to indicate which
    one it is.
    """

    def __init__(self, message):
        """Constructor

        :param str message: message to show
        """
        self.message = message
        self.field = None
        self.field_id = None

    def __str__(self):
        if self.field and self.field_id:
            return '{} (field #{}): {}'.format(self.field, self.field_id,
                                               self.message)
        else:
            return self.message


class Field:
    """
    Single field of data

    Subclasses must override ``to_python``, which should convert provided data
    as string to Python type equivalent, possibly doing some validation as
    well.
    """

    def __init__(self, empty=False, ignored=False, optional=False,
                 dict_included=True, choices=None):
        """Constructor

        :param bool empty: whether or not the value can be empty
        :param bool ignored: whether or not the value in this field is ignored
            by the parser
        :param bool optional: whether or not the value is optional (i.e. it may
            be omitted). Note that the optional fields might be placed only at
            the end.
        :param bool dict_included: whether or not this field should be included
            in the value returned by ``SerializerData.as_dict`` method. Note
            that ignored fields always has ``dict_included=False``.
        :param list|tuple choices: list of valid field values
        """
        self.empty = empty
        self.ignored = ignored
        self.optional = optional
        self.dict_included = dict_included if not ignored else False
        self.choices = choices

    def to_python(self, data):
        """Convert provided data as string to Python type

        Subclasses must override this method and may raise ``ValidationError``
        in case of invalid values.

        :param str data: data to convert
        :return: parsed value
        """
        raise NotImplementedError

    def get_value(self, data):
        """Get converted value of data

        :param str data: data to convert
        :return: parsed value or None if data is empty
        :raise ValidationError: if data is empty, but ``empty`` parameter
            for ``__init__`` was specified as ``False``
        """
        if not data:
            if self.empty:
                return None
            else:
                raise ValidationError('Got empty content, but empty=False')

        if self.choices is not None and data not in self.choices:
            raise ValidationError("Parsed value: '{}' is not any of valid "
                                  "choices: {}"
                                  .format(data, list(self.choices)))

        return self.to_python(data)


class StringField(Field):
    """Field for storing string values"""

    def to_python(self, data):
        return data


class IgnoredField(StringField):
    """
    Field that is explicitly ignored. ``empty`` attribute is specified as
    ``True`` by default.
    """

    def __init__(self, empty=True, *args, **kwargs):
        super().__init__(empty=empty, ignored=True, *args, **kwargs)


class IntegerField(Field):
    """Field for storing integer values"""

    def to_python(self, data):
        try:
            return int(data)
        except ValueError:
            raise ValidationError('Invalid integer value: {}'.format(data))


class FloatField(Field):
    """Field for storing float values"""

    def to_python(self, data):
        try:
            return float(data)
        except ValueError:
            raise ValidationError('Invalid float value: {}'.format(data))
