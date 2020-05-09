import sys
import datetime
from tabulate import tabulate
from .sync import JiraSync
from .worklog import JiraWorklog


class Jira:
    """
    Class responsible for creating Jira worklogs
    and syncing worklogs with Jira system
    """

    def __init__(self, prepared_entities, dry_run=False):
        self._DEFAULT_START_TIME = '08:00:00'
        self.prepared_entities = prepared_entities
        self.worklogs = []
        self.worklogs_to_render = []
        self._projects = []
        self._dry_run = dry_run

        self.prepare_worklogs_from_entities()
        self._check_for_duplicate_projects()

    def _check_for_duplicate_projects(self):
        if len(self._projects) > 1:
            print('There has been found more projects: {}'.format(', '.join(self._projects)))
            sync_all_answer = input('Do you want to sync them all ? (y/n): ')
            while sync_all_answer.lower() not in ('y', 'yes', 'n', 'no'):
                sync_all_answer = input('Do you want to sync them all ? (y/n)')
            if sync_all_answer.lower() in ('y', 'yes'):
                return True

            project_to_sync = input('Which project do you wan to sync ? [write it please]: ')
            while project_to_sync not in self._projects:
                project_to_sync = input('Project not found. Please write one of found projects: ')

            for worklog in self.worklogs:
                if worklog.get_project() == project_to_sync:
                    continue
                self.worklogs.remove(worklog)
        return True

    def prepare_worklogs_from_entities(self):
        for entity in self.prepared_entities:
            if entity.project not in self._projects:
                self._projects.append(entity.get_project())
            worklog = JiraWorklog(entity)
            self.worklogs.append(worklog)
            self.worklogs_to_render.append(worklog.get_raw_worklog())

    def sync_data(self):
        sync_method = '0'
        while int(sync_method) not in range(1, 4):
            sync_method = input(
                '\nDo you want to sync all data or merged data ? \n'
                '  1) All data: Will sync data exactly how they were tracked in Time Doctor ( tested with API ) \n'
                '  2) Merged data: Records will be merged by task and added to jira by task ( tested with File )\n'
                '  3) Exit\n\n'
                'Your answer: ')
        if sync_method == '3':
            sys.exit('Exiting ...')
        sync = JiraSync(self._dry_run)
        if sync_method == '1':
            print('Merging by "All data" method \n')
            sync.sync_all_data(self.worklogs)
        if sync_method == '2':
            print('Merging by "Merged data" method ')
            sync.sync_merged_data(self._get_merged_worklogs_by_date())

    def show_data_to_sync(self):
        headers = ['Issue key', 'Date', 'Duration', 'Description']
        print(tabulate(self.worklogs_to_render, tablefmt='fancy_grid', headers=headers))

    def print_merged_logs(self):
        """
        Based on given data renders data to table
        """
        merged_logs = self._get_merged_worklogs_by_date()
        for date in merged_logs:
            day_table = []
            day_total_time = 0
            for issue_key in merged_logs[date]:
                worklog = merged_logs[date][issue_key]
                raw_worklog = worklog.get_raw_worklog()
                day_total_time += float(worklog.get_duration())
                day_table.append(raw_worklog)

            print('Worklogs for {}. ( total day time {} )'.format(date, day_total_time))
            print(tabulate(day_table, tablefmt='fancy_grid'))

    def _get_merged_worklogs_by_date(self):
        merged_logs = {}
        for worklog in self.worklogs:
            date_identifier = worklog.get_date()
            key_identifier = worklog.get_issue_key()

            if date_identifier not in merged_logs:
                merged_logs[date_identifier] = {}

            actual_date = merged_logs[date_identifier]

            if key_identifier not in actual_date:
                actual_date[key_identifier] = worklog
            else:
                actual_date[key_identifier] = actual_date[key_identifier].merge_with_another_worklog(worklog)

        return self._set_start_times_for_merged_logs(merged_logs)

    def _set_start_times_for_merged_logs(self, merged_logs):
        """
        Sets start time for one record as previous record ended

        :param merged_logs:
        :return:
        """
        for day in merged_logs:
            day_logs = merged_logs[day]
            previous_end_time = None
            for worklog_key in day_logs:
                worklog = day_logs[worklog_key]
                if previous_end_time is None:
                    # First issue of a day
                    hours, minutes, seconds = self._DEFAULT_START_TIME.split(':')
                    first_start_time = datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
                    worklog.set_start_time(str(first_start_time))
                    previous_end_time = first_start_time.seconds + int(worklog.get_duration())
                    continue
                # Standard issue of a day
                new_start_time = datetime.timedelta(seconds=previous_end_time)
                worklog.set_start_time(str(new_start_time))
                previous_end_time += int(worklog.get_duration())

        return merged_logs
