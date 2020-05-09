import csv
import re
from os import path
from pathlib import Path
from .config import Config


class Mapper:
    """
    Class responsible for map not exact Time doctor descriptions
    to JIRA tasks. Class creates CSV mapping files with 2 columns:
        * keyword
        * task number
    """

    def __init__(self):
        self._MAPPING_FILE = 'data/tasks_mapping.csv'
        self.config = Config()
        self.saved_mappings = {}
        self._check_mapping_file()
        self._load_saved_mappings()

    def _check_mapping_file(self):
        if not path.exists(self._MAPPING_FILE):
            print('[ info ] Mapping file does not exists.')
            Path(self._MAPPING_FILE).touch()
            print('[ info ] Mapping file successfully created.')

    def _load_saved_mappings(self):
        with open(self._MAPPING_FILE, 'r') as map_file:
            reader = csv.reader(map_file)
            for row in reader:
                self.saved_mappings[row[0]] = row[1]

    def get_mapped_task(self, description):
        """
        Split given description based on configured delimiter. If delimiter is
        not in use, description will be split based on space

        :param description:
        :return:
        """
        if self.config.use_delimiter():
            delimiter = self.config.get_delimiter()
        else:
            delimiter = ' '
        split_desc = description.split(delimiter)
        first_key_part = split_desc[0]

        if first_key_part in self.saved_mappings:
            return self.saved_mappings[first_key_part]

        print('Task {} not mapped.'.format(split_desc))
        issue_nr = input('Please map issue number to description: {}-'.format(self.config.get_project_key()))

        while not re.search('[0-9]+', issue_nr):
            print('Invalid issue nr.')
            issue_nr = input('Please map issue number to description: {}-'.format(self.config.get_project_key()))

        with open(self._MAPPING_FILE, 'a') as map_file:
            writer = csv.writer(map_file)
            writer.writerow([first_key_part, issue_nr])
            print('Issue mapping saved successfully ...')

        return issue_nr
