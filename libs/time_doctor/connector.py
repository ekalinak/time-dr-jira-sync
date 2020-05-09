import requests
import json
import re
from .config import Config
from .exceptions import ConnectorException


class Connector:
    """
    Class responsible for getting data
    from TimeDoctor via API
    """

    def __init__(self):
        # Variables
        self.temp_variables = {
            'client_id': '2411_4rzqimlvoco4kg0gc8c0s00c80wkwwogg04o8w4k84ckck8c0c',
            'secret_key': '5nsgg52ztls0owwocwc0kks0sw0ww84wsoggw04oo40844o00o'
        }
        self._TOKEN_AUTH_URL = 'https://webapi.timedoctor.com/oauth/v2/auth_login'
        self._DOCUMENTATION_LINK = 'https://webapi.timedoctor.com/doc#documentation'
        self._API_URL = 'https://webapi.timedoctor.com/v1.1/'
        self._API_METHODS = {
            'user': 'companies',
            'worklogs': 'companies/{}/worklogs'
        }
        self._CACHE_DAY = 'day'
        self._CACHE_RANGE = 'range'
        self._DATE_FORMAT = '[0-9]{4}-[01][1-2]-[0-3][0-9]'
        self._loaded_data = {}
        self._cache_values = {self._CACHE_DAY: '', self._CACHE_RANGE: []}
        self.config = Config()

        # Init methods
        self._user = self._get_user_data()

    def _get_user_data(self):
        api_response = self._make_request(self._API_METHODS['user'])
        return api_response['user']

    def _make_request(self, api_method, params=None):
        if params is None:
            params = {}
        api_token = self.config.get_api_token()
        url = self._API_URL + api_method

        if '_format' not in params:
            params['_format'] = 'json'
        params['access_token'] = api_token
        response = requests.get(url, params=params)
        json_response = json.loads(response.text)
        if response.status_code == 401:
            self.config.invalidate_api_token()
            raise ConnectorException(
                   '\nAPI connection problem. ( Reason: {} ) \n '
                   'Try to refresh your ACCESS TOKEN visit {} and click "Get Your Access Token'.format(
                       response.reason, self._DOCUMENTATION_LINK)
               )
        if response.status_code != 200:
            raise ConnectorException(
                'Not successful response from TimeDoctor API \n\n'
                'Status: {}, \nError: {} \nError Description: {}'.format(
                    response.status_code, json_response['error'], json_response['error_description']))
        return json_response

    def _get_user_id(self):
        return self._user['id']

    def _get_company_id(self):
        return self._user['company_id']

    def _get_range_value(self):
        cached_range = self._cache_values[self._CACHE_RANGE]
        if isinstance(cached_range, list):
            cached_range = []
        if len(cached_range) == 2:
            use_cached_range = self._yes_no_question('Do you want to use already used range ?')
            if use_cached_range:
                return cached_range

        start_date = self._get_date_value('Enter start date : ')
        end_date = self._get_date_value('Enter end date: ')
        self._cache_values[self._CACHE_RANGE] = [start_date, end_date]
        return self._cache_values[self._CACHE_RANGE]

    def _get_day_value(self):
        """
        Returns day, for which worklogs should be retrieved. Working
        also with cache value ( cache_day )

        :return: str
        """
        cached_day = self._cache_values[self._CACHE_DAY]
        if len(cached_day):
            day = cached_day
            if not self._yes_no_question('Do you want to use {} day'.format(cached_day)):
                day = self._get_date_value('Please enter day you want to get worklogs: ')
        else:
            day = self._get_date_value('Please enter day you want to get worklogs: ')
            self._cache_values[self._CACHE_DAY] = day
        return day

    def _get_date_value(self, question):
        date_value = input(question)
        while re.match(self._DATE_FORMAT, date_value) or not len(date_value):
            print('Wrong format ( "YYYY-MM-DD" required ')
            date_value = input(question)

        return date_value

    def _yes_no_question(self, question):
        positive_answer = ' ( y/n [yes/no] ) '
        answer = input(question + positive_answer)
        if answer.lower() in ('y', 'yes'):
            return True
        return False

    def get_user_day_worklogs(self):
        """
        Gets users worklogs for given day.

        :return:
        """
        company_id = self._get_company_id()
        api_endpoint = self._API_METHODS['worklogs'].format(company_id)

        day = self._get_day_value()

        if day in self._loaded_data:
            return self._loaded_data[day]
        params = {'start_date': day, 'end_date': day, 'user_ids': self._get_user_id(), 'consolidated': 0}
        api_response = self._make_request(api_endpoint, params)
        self._loaded_data[day] = api_response['worklogs']['items']
        return self._loaded_data[day]

    def get_user_range_worklogs(self):
        company_id = self._get_company_id()
        api_endpoint = self._API_METHODS['worklogs'].format(company_id)

        date_range = self._get_range_value()
        range_id = '-'.join(date_range)
        if range_id in self._loaded_data:
            return self._loaded_data[range_id]

        params = {'start_date': date_range[0], 'end_date': date_range[1], 'user_ids': self._get_user_id(), 'consolidated': 0}
        api_response = self._make_request(api_endpoint, params)
        self._loaded_data[range_id] = api_response['worklogs']['items']

        return self._loaded_data[range_id]
