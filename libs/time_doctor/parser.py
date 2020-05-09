import csv
from .parserexception import ParserException
from .entity import TimeDoctorEntity
from os import path


class TimeDoctorParser:
    """
    Class responsible for parsing raw data from input
    and creating TimeDoctorEntity objects
    """

    def __init__(self, raw_data, from_file=True):
        self.parsed_entities = []
        if from_file:
            self._parse_file_data(raw_data)
        else:
            self._parse_api_data(raw_data)

    def _parse_file_data(self, raw_data_file):
        if not path.exists(raw_data_file):
            raise ParserException('Given file does not exists: {}'.format(raw_data_file))

        with open(raw_data_file, 'r') as csv_file:
            data_reader = csv.reader(csv_file)
            next(data_reader)  # Ignore header
            for row in data_reader:
                self.parsed_entities.append(TimeDoctorEntity(row))

    def _parse_api_data(self, raw_data):
        for record in raw_data:
            self.parsed_entities.append(TimeDoctorEntity(record))

    def get_time_doctor_entities(self):
        """
        Return parsed entities in list

        :return: list
        """
        return self.parsed_entities
