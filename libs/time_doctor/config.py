import csv
from os import path
from pathlib import Path


class Config:
    """
    Class responsible for TimeDoctor configuration. Configuration is in CSV file
    with key => value pair
    """

    def __init__(self):
        # Variables
        self._API_TOKEN = 'api_token'
        self._OLD_API_TOKEN = 'old_api_token'
        self._CONFIG_FILE = 'data/td-config.csv'
        self._REQUIRED_CONFIG = [self._API_TOKEN]
        self._OPTIONAL_CONFIG = [self._OLD_API_TOKEN]
        self._loaded_config = {}

        # Init methods
        self._check_config_file()
        self._load_configuration()

    def _check_config_file(self):
        """
        Check configuration file. In case it does not exists, it will create one.

        :return: bool
        """
        config_file_path = self._get_config_file_path()
        if not path.exists(config_file_path):
            self._create_config_file()
            return True
        return True

    def _load_configuration(self):
        with open(self._CONFIG_FILE, 'r') as config_file:
            conf_file = csv.reader(config_file)
            for row in conf_file:
                self._loaded_config[row[0]] = row[1]

    def _get_config_file_path(self):
        """
        Returns location of configuration file

        :return:
        """
        return self._CONFIG_FILE

    def _create_config_file(self):
        """
        Creates configuration file

        :return: bool
        """
        config_file_path = self._get_config_file_path()
        try:
            # Create file
            Path(config_file_path).touch()
            print('[ info ]: TimeDoctor configuration file created ...')
        except Exception as e:
            print(e)
            return False
        return True

    def get_api_token(self):
        """
        Return saved token

        :param config_key:
        :return:
        """
        if self._API_TOKEN in self._loaded_config and len(self._loaded_config[self._API_TOKEN]):
            return self._loaded_config[self._API_TOKEN]

        print('TimeDoctor API token was not configured yet.Please visit https://webapi.timedoctor.com/doc#documentation'
              ' and click on "Get Your Access Token "')

        api_token = ''

        while not len(api_token):
            api_token = input('Please enter your API token: ')

        self._loaded_config[self._API_TOKEN] = api_token
        with open(self._CONFIG_FILE, 'a') as config_file:
            conf_file = csv.writer(config_file)
            conf_file.writerow([self._API_TOKEN, api_token])
        return api_token

    def invalidate_api_token(self):
        self._loaded_config[self._OLD_API_TOKEN] = self._loaded_config[self._API_TOKEN]
        self._loaded_config[self._API_TOKEN] = ''
        config_to_save = []
        for key in self._loaded_config:
            config_to_save.append([key, self._loaded_config[key]])

        with open(self._CONFIG_FILE, 'w') as config_file:
            conf_file = csv.writer(config_file)
            conf_file.writerows(config_to_save)
        print('[ info ] Previous API token successfully invalidated ...')
        return True
