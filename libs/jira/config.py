import csv
import json
import requests
from os import path
from pathlib import Path
from termcolor import colored
from .exceptions.configexception import ConfigException


class Config:
    """
    Class responsible for handling config
    for whole "sync" script.
    """

    def __init__(self):
        self._CONFIG_FILE = 'data/jira-config.csv'

        self._CONFIG_PROJECT_ID = 'project_id'
        self._CONFIG_JIRA_BASE_URL = 'jira_base_url'
        self._CONFIG_JIRA_USER_API_KEY = 'jira_user_api_key'
        self._CONFIG_JIRA_USER_LOGIN = 'jira_user_login'
        self._CONFIG_TEMPO_API_KEY = 'tempo_api_key'

        self._CONFIG_JIRA_ACCOUNT_ID = 'jira_user'
        self._CONFIG_LOGICAL_DELIMITER = 'logical_delimiter'

        self._TEMPO_API_URL = 'https://api.tempo.io/core/3/'
        self._JIRA_ACCOUNT_ENDPOINT = 'wiki/rest/api/user/current'
        self._TEMPO_WORKLOGS_ENDPOINT = 'worklogs'
        self._JIRA_PROJECTS_ENDPOINT = 'rest/api/3/project'
        self.COLORS = {
            'error_bgr': 'on_red',
            'error_txt': 'grey',
            'info_bgr': 'on_yellow',
            'info_txt': 'grey'
        }

        self._loaded_config = {}

        if not path.exists(self._CONFIG_FILE):
            print(colored('[ warning ] Config file not created.', self.COLORS['info_txt'], self.COLORS['info_bgr']))
            Path(self._CONFIG_FILE).touch()
            print(colored('[ info ] Empty config file created successfully.', self.COLORS['info_txt'],
                          self.COLORS['info_bgr']))

        self._load_config()

    def _load_config(self):
        with open(self._CONFIG_FILE, 'r') as config_file:
            reader = csv.reader(config_file)
            for row in reader:
                self._loaded_config[row[0]] = row[1]

    def _write_config(self, key, value, success_msg=''):
        """
        Writes configuration to config file based on key / value. You can optinally
        pass message after success configuration save

        :param key:
        :param value:
        :param success_msg:
        :return:
        """
        with open(self._CONFIG_FILE, 'a') as config_file:
            writer = csv.writer(config_file)
            writer.writerow([key, value])
            if len(success_msg):
                print(success_msg)
            else:
                print('\n[ info ] {} successfully saved ( value "{}" )...\n'.format(key, value))

    def _process_config_value(self, key, value, message=''):
        """
        Saves config key with value to config file + set them to loaded config + returns value of config

        :param key:
        :param value:
        :param message:
        :return:
        """
        self._write_config(key, value, message)
        self._loaded_config[key] = value
        return value

    def get_project_key(self):
        if self._CONFIG_PROJECT_ID in self._loaded_config:
            return self._loaded_config[self._CONFIG_PROJECT_ID]

        base_url = self.get_jira_base_url()
        projects_endpoint = self._JIRA_PROJECTS_ENDPOINT
        user = self.get_jira_user_login()
        api_token = self.get_jira_user_api_key()
        response = requests.get(base_url + projects_endpoint, auth=(user, api_token))
        parsed_projects = json.loads(response.text)
        if len(parsed_projects) == 1:
            project_key = parsed_projects[0].get('key')
            return self._process_config_value(self._CONFIG_PROJECT_ID, project_key)

        print('Please choose which project you want to sync: ')
        for key, value in enumerate(parsed_projects):
            print('\t{}) {}'.format(key + 1, parsed_projects[key].get('key')))

        project_to_save = -1
        while int(project_to_save) not in range(1, len(parsed_projects) + 1):
            project_to_save = input('Your choice: ')

        project_key = parsed_projects[int(project_to_save) - 1].get('key')
        return self._process_config_value(self._CONFIG_PROJECT_ID, project_key)

    def get_tempo_api_url(self):
        return self._TEMPO_API_URL

    def get_tempo_api_key(self):
        """
        Returns tempo API key. If not stored in configuration, it will ask for it

        :return:
        """
        if self._CONFIG_TEMPO_API_KEY in self._loaded_config:
            return self._loaded_config['tempo_api_key']

        print('Tempo API key not yet defined. You can get your Tempo API key here: '
              '{}plugins/servlet/ac/io.tempo.jira/tempo-configuration#!/api-integration or navigate to '
              '"Apps > Tempo > Settings > User Preferences > API Integrations'.format(self.get_jira_base_url()))

        tempo_api_key = ''
        while not len(tempo_api_key):
            tempo_api_key = input('Please enter your Tempo API key:')

        return self._process_config_value(self._CONFIG_TEMPO_API_KEY, tempo_api_key)

    def get_tempo_worklogs_endpoint(self):
        return self._TEMPO_WORKLOGS_ENDPOINT

    def use_delimiter(self):
        """
        Returns true in case user wants to use logical delimiter for parsing issues

        :return:
        """
        delimiter = self.get_delimiter()
        if delimiter:
            return True
        return False

    def get_delimiter(self):
        """
        Returns logicla delimiter. In case logical delimiter is not defined, it will asks for one
        :return:
        """
        if self._CONFIG_LOGICAL_DELIMITER in self._loaded_config:
            if self._loaded_config[self._CONFIG_LOGICAL_DELIMITER] == '0':
                return False
            return self._loaded_config[self._CONFIG_LOGICAL_DELIMITER]

        be_logical = ''

        while be_logical.lower() not in ('y', 'n', 'yes', 'no'):
            be_logical = input('Do you want to define logical delimiter ? [y/n]')

        if be_logical.lower() in ('n', 'no'):
            self._process_config_value(self._CONFIG_LOGICAL_DELIMITER, '0')
            return False

        logical_delimiter = ''
        while not len(logical_delimiter):
            logical_delimiter = input('Please enter logical delimiter: ')

        return self._process_config_value(self._CONFIG_LOGICAL_DELIMITER, logical_delimiter)

    def get_jira_base_url(self):
        if self._CONFIG_JIRA_BASE_URL in self._loaded_config:
            return self._loaded_config[self._CONFIG_JIRA_BASE_URL]

        base_url = ''
        while not len(base_url):
            base_url = input('Please enter Jira base url of your project. ( i.e. "[project].atlassian.net/"): ')

        if base_url[-1] != '/':
            base_url += '/'

        self._write_config(self._CONFIG_JIRA_BASE_URL, base_url)
        self._loaded_config[self._CONFIG_JIRA_BASE_URL] = base_url

        return base_url

    def get_jira_user_login(self):
        """
        Returns Jira login name from configuration. If not saved in configuration, it asks for it and save.
        :return:
        """
        if self._CONFIG_JIRA_USER_LOGIN in self._loaded_config:
            return self._loaded_config[self._CONFIG_JIRA_USER_LOGIN]

        print('Jira login not configured yet. User login is usually email, which you are logging to Jira')
        user_login = ''
        while not len(user_login):
            user_login = input('Please enter Jira login: ')

        return self._process_config_value(self._CONFIG_JIRA_USER_LOGIN, user_login)

    def get_jira_user_api_key(self):
        """
        Returns JIRA API token. In case token is not saved in configuration, method asks for it.
        :return:
        """
        if self._CONFIG_JIRA_USER_API_KEY in self._loaded_config:
            return self._loaded_config[self._CONFIG_JIRA_USER_API_KEY]

        print('Jira API key not defined. You can get Jira API key from URL '
              'https://id.atlassian.com/manage-profile/security/api-tokens or navigate from your Jira: '
              'Account Settings > Security > API teoken > Create and manage API tokens')

        api_token = ''
        while not len(api_token):
            api_token = input('Please enter your Jira API token: ')

        return self._process_config_value(self._CONFIG_JIRA_USER_API_KEY, api_token)

    def get_jira_user_account_id(self):
        if self._CONFIG_JIRA_ACCOUNT_ID in self._loaded_config:
            return self._loaded_config[self._CONFIG_JIRA_ACCOUNT_ID]

        base_url = self.get_jira_base_url()
        user_endpoint = self._JIRA_ACCOUNT_ENDPOINT

        user = self.get_jira_user_login()
        api_token = self.get_jira_user_api_key()
        response = requests.get(base_url + user_endpoint, auth=(user, api_token))
        if response.status_code != 200:
            raise ConfigException('Failed to get info about Jira account')
        response = json.loads(response.text)

        account_id = response.get('accountId')
        if not account_id:
            raise ConfigException('Failed to retrieve account ID')

        return self._process_config_value(self._CONFIG_JIRA_ACCOUNT_ID,
                                          account_id,
                                          '\n[ info ] Account ID successfully retrieved and saved ...\n')
