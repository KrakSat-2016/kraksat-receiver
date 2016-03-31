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
    To append Kundt's tube measurement, append to kundt list;
    when no new measurement is going to be send set is_kundt_ready flag
    """
    def __init__(self):
        self.data = []
        self.current_record = None
        self.current_timestamp = None

        self.kundt = []
        self.is_kundt_ready = False

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
            self.current_record = CollectorRecord()
        self.current_timestamp = timestamp
        self.current_record.timestamp = timestamp
        setattr(self.current_record, key, value)

    def get_iter(self, *args):
        for record in self.data:
            if len(args) == 1:
                res = getattr(record, args[0])
                if res is None:
                    continue
            else:
                res = tuple(getattr(record, key) for key in args)
                if any(map(lambda x: x is None, res)):
                    continue
            yield res

    def get_ground_pressure(self):
        pressure = []
        for i in self.data[-3:]:
            pressure.append(i.pressure)
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
        return statistics.median(acceleration)

    def get_average_temperature(self):
        numerator, denominator = 0, 0
        for temp, timestamp in self.get_iter('temperature', 'timestamp'):
            if (self.landing_timestamp is not None and
                    timestamp > self.landing_timestamp):
                break
            numerator += temp
            denominator += 1
        return numerator / denominator
