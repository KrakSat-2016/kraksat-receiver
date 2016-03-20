import statistics


class CollectorRecord:
    __slots__ = ['acceleration', 'altitude', 'temperature', 'timestamp',
                 'pressure']

    def __init__(self):
        self.acceleration = None
        self.altitude = None
        self.temperature = None
        self.timestamp = None
        self.pressure = None


class Collector:
    """
    Collect data for scientific computations.
    """
    def __init__(self):
        self.data = []
        self.current_record = None
        self.current_timestamp = None

    def add_value(self, timestamp, key, value):
        """
        add new measurement
        :param timestamp: timestamp of measurement
        :param key: key on witch value will be stored
        :param value: measurement value
        """
        if timestamp != self.current_timestamp:
            if self.current_record is not None:
                self.data.append(self.current_record)
            self.current_record = CollectorRecord
        self.current_timestamp = timestamp
        self.current_record.timestamp = timestamp
        setattr(self.current_record, key, value)

    def get_iter(self, *keys):
        return CollectorIterator(self, keys)

    def get_ground_pressure(self):
        pressure = []
        for i in self.data[-6:]:
            pressure.append(i.pressure)
        return statistics.median(pressure)


class CollectorIterator:
    def __init__(self, obj, keys):
        self.keys = keys
        self.n = -1
        self.obj = obj

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.n += 1
            try:
                current_record = self.obj.data[self.n]
            except IndexError:
                raise StopIteration
            try:
                if self.keys.__len__() == 1:
                    return getattr(current_record, self.keys[0])
                return tuple(getattr(current_record, i) for i in self.keys)
            except AttributeError:
                pass
