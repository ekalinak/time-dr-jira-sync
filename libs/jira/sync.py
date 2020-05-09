import time
import requests
import datetime
from tqdm import tqdm
from tabulate import tabulate
from .config import Config
from .exceptions.syncexception import SyncException


class JiraSync:
    """
    Class responsible for syncing JiraWorklogs
    objects with Jira system itself.
    """

    def __init__(self, dry_run):
        self._ACCOUNT_API_LINK = 'https://gymbeam.atlassian.net/wiki/rest/api/user/current'
        self.config = Config()
        self._dry_run = dry_run

    def _sync_data(self, worklogs_data):
        """
        Expects dictionary of worklogs where key in dictionary is issue key

        :param worklogs_data: dict
        :return: void
        """
        url = self.config.get_tempo_api_url() + self.config.get_tempo_worklogs_endpoint()
        headers = {'Authorization': 'Bearer {}'.format(self.config.get_tempo_api_key())}
        for issue in worklogs_data:
            worklog = worklogs_data[issue]

            data_to_send = {
                'startTime': '9:00:00',
                'issueKey': '{}-{}'.format(self.config.get_project_key(), worklog.get_issue_key()),
                'timeSpentSeconds': worklog.get_duration_in_seconds(),
                'billableSeconds': worklog.get_duration_in_seconds(),
                'startDate': worklog.get_date(),
                'description': worklog.get_description(),
                'authorAccountId': self.config.get_jira_user_account_id()

            }
            if self._dry_run:
                print('Data synced. Respone was {}'.format('200'))
                time.sleep(0.75)
            else:
                response = requests.post(url, json=data_to_send, headers=headers)
                print('Data synced. Respone was {}'.format(response))
        print('All worklogs synced ...')

    def sync_all_data(self, data_to_sync):
        url = self.config.get_tempo_api_url() + self.config.get_tempo_worklogs_endpoint()
        headers = {'Authorization': 'Bearer {}'.format(self.config.get_tempo_api_key())}
        print('Progress: \n')
        for worklog in tqdm(data_to_sync):
            if isinstance(data_to_sync, dict):
                worklog = data_to_sync[worklog]
            data_to_send = {
                'startTime': worklog.get_start_time(),
                'issueKey': '{}-{}'.format(self.config.get_project_key(), worklog.get_issue_key()),
                'timeSpentSeconds': worklog.get_duration(),
                'billableSeconds': worklog.get_duration(),
                'startDate': worklog.get_date(),
                'description': worklog.get_description(),
                'authorAccountId': self.config.get_jira_user_account_id()

            }

            if self._dry_run:
                time.sleep(0.75)
            else:
                response = requests.post(url, json=data_to_send, headers=headers)
                if response.status_code != 200:
                    print('Warning: Response status {} for record: {} ( Date: {}, Start time: {} )'.format(
                        response.status_code,
                        data_to_send.get('issueKey'),
                        data_to_send.get('startDate'),
                        data_to_send.get('startTime')))

        print('Worklogs syncing finished !')

    def sync_merged_data(self, data_to_sync):
        for day in data_to_sync:
            print('\nSyncing data for {}'.format(day))
            table_data = []
            for issue_key in data_to_sync[day]:
                raw_worklog = data_to_sync[day][issue_key].get_raw_worklog()
                headers = ['Issue Key', 'Date', 'Start Time', 'Duration', 'Task description']
                raw_worklog[0] = '-'.join([self.config.get_project_key(), raw_worklog[0]])
                duration_format = datetime.timedelta(seconds=int(raw_worklog[3]))
                raw_worklog[3] = str(duration_format)
                table_data.append(raw_worklog)
            print(tabulate(table_data, tablefmt='fancy_grid', headers=headers))
            confirm = input('Do yo want to sync those data ? ')
            if confirm.lower() in ('n', 'no'):
                print('Not syncing. Skipping ...')
                continue

            self.sync_all_data(data_to_sync[day])
