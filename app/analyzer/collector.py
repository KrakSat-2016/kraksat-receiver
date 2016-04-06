import statistics


class NoDataError(Exception):
    """
    Raised when there is insufficient data to perform requested calculation.
    """
    pass


class CollectorRecord:
    __slots__ = ['acceleration', 'altitude', 'temperature', 'timestamp',
                 'pressure']

    def __init__(self):
        self.acceleration = None
        self.altitude = None
        self.temperature = None
        self.timestamp = None
        self.pressure = None

    def __repr__(self):
        return 'CollectorRecord({})'.format(
            ', '.join(str(getattr(self, attr)) for attr in self.__slots__))


class Collector:
    """
    Collect data for scientific computations.
    To append Kundt's tube measurement, append to kundt list;
    when no new measurement is going to be send set is_kundt_ready flag

    Note that the implementation of Collector is not thread-safe.
    """
    def __init__(self):
        self.data = []
        self.current_record = None
        self.current_timestamp = None

        self.kundt = []

        self.landing_timestamp = None

    def add_value(self, timestamp, key, value):
        """
        Add new measurement
        :param timestamp: timestamp of measurement
        :param key: key on witch value will be stored
        :param value: measurement value
        """
        if timestamp != self.current_timestamp:
            if self.current_record is not None:
                self.data.append(self.current_record)
                self._data_modified()
            self.current_record = CollectorRecord()
        self.current_timestamp = timestamp
        self.current_record.timestamp = timestamp
        setattr(self.current_record, key, value)

    def _data_modified(self):
        """Called whenever some data is added

        May be overridden by subclasses to e.g. re-run calculation.
        """
        pass

    def get_iter(self, *args):
        for record in self.data:
            res = tuple(getattr(record, key) for key in args)
            if any(map(lambda x: x is None, res)):
                continue
            if len(res) == 1:
                yield res[0]
            else:
                yield res

    def get_ground_pressure(self):
        pressure = []
        for i in self.data[-3:]:
            pressure.append(i.pressure)
        if len(pressure) == 0:
            raise NoDataError('No pressure data')
        # To avoid big measurement errors use median instead of last point
        return statistics.median(pressure)

    def get_average_acceleration(self):
        # If can is still flying use median of all measurements,
        # otherwise use last 10 measurements
        if self.landing_timestamp is None:
            return statistics.median(self.get_iter('acceleration'))
        acceleration = []
        for i in self.data[-10:]:
            acceleration.append(i)
        if len(acceleration) == 0:
            raise NoDataError('No acceleration data')
        return statistics.median(acceleration)

    def get_average_temperature(self):
        numerator, denominator = 0, 0
        for temp, timestamp in self.get_iter('temperature', 'timestamp'):
            if (self.landing_timestamp is not None and
                    timestamp > self.landing_timestamp):
                break
            numerator += temp
            denominator += 1
        if denominator == 0:
            raise NoDataError('No temperature data')
        return numerator / denominator
