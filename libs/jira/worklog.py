import re
from .config import Config
from .mapper import Mapper
from .exceptions.worklogexception import JiraWorklogException


class JiraWorklog:
    """
    Class represents Jira Worklog entity. This
    entity can be sent to Jira to create regular
    Jira time entry ( worklog )
    """

    def __init__(self, time_doctor_entity):
        # class dependencies
        self._config = Config()
        self._mapper = Mapper()

        # class porperties
        self.duration = float(time_doctor_entity.get_duration())
        self.date = time_doctor_entity.get_date()
        self.start_time = time_doctor_entity.get_start_date()
        self.description = time_doctor_entity.get_description()
        self.issue_key = self._parse_issue_key(time_doctor_entity.get_description())
        self.project = time_doctor_entity.get_project()

    def _parse_issue_key(self, description_string):
        project_id = self._config.get_project_key()
        key_candidate = re.findall(project_id + '-([0-9]+)', description_string)

        if len(key_candidate):
            return key_candidate[0]

        return self._mapper.get_mapped_task(description_string)

    def get_raw_worklog(self):
        return [self.issue_key, self.date, self.start_time, self.duration, self.description]

    def get_project(self):
        return self.project

    def get_issue_key(self):
        return self.issue_key

    def get_date(self):
        return self.date

    def get_duration(self):
        return self.duration

    def get_duration_in_seconds(self):
        return float(self.duration) * 60 * 60

    def get_description(self):
        return self.description

    def get_start_time(self):
        return self.start_time

    def set_start_time(self, start_time):
        self.start_time = start_time

    def merge_with_another_worklog(self, worklog):
        if worklog.get_date() != self.get_date():
            raise JiraWorklogException('Worklogs are not from same date. Can\'t merge worklogs from two days. '
                                       'Please try to merge logs only from one day.')
        self.duration = float(self.duration) + float(worklog.get_duration())
        desc_already_found = re.findall(worklog.description, self.description)
        if worklog.get_description().find(self.description) == -1:
            self.description = self._merge_worklogs_descriptions(self.description, worklog.get_description())

        # if not len(desc_already_found):
        #     self.description = self._merge_worklogs_descriptions(self.description, worklog.get_description())
        return self

    def _merge_worklogs_descriptions(self, description, new_part):
        delimiter = ''
        if self._config.use_delimiter():
            delimiter = self._config.get_delimiter()
        if len(delimiter):
            new_desc_parts = new_part.split(delimiter)
            not_mentioned_parts = []
            for part in new_desc_parts:
                if description.find(part.strip()) == -1:
                    not_mentioned_parts.append(part)
            if not len(not_mentioned_parts):
                return description  # Nothing new found
            new_part = ': '.join(not_mentioned_parts)

        if description.find(new_part) == -1:
            description = description + '\n' + new_part

        return description
