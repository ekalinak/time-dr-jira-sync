from .parser import TimeDoctorParser


class TimeDoctor:
    """
    Class responsible for processing raw input
    from exported Time Doctor file and gather
    all data as TimeDoctorEntities
    """

    def __init__(self, data_input, from_file=True):
        parser = TimeDoctorParser(data_input, from_file)
        self.parsed_data = parser.get_time_doctor_entities()

    def get_parsed_data(self):
        return self.parsed_data
