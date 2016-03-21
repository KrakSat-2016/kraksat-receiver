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
            self.current_record = CollectorRecord()
        self.current_timestamp = timestamp
        self.current_record.timestamp = timestamp
        setattr(self.current_record, key, value)

    def get_iter(self, *args):
        for record in self.data:
            if args.__len__() == 1:
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
        for i in self.data[-6:]:
            pressure.append(i.pressure)
        return statistics.median(pressure)
