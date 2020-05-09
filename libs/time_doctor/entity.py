class TimeDoctorEntity:
    """
    Class represent one time doctor entity ( from manually exported data )
    It's time doctor entry for one issue per day
    """

    def __init__(self, raw_entity_data):
        self.user = ''
        self.description = ''
        self.date = ''
        self.project = ''
        self.start_date = ''
        self.end_date = ''
        self.duration_human_readable = ''
        self.duration = ''
        self.device = ''

        if self.is_data_from_api(raw_entity_data):
            self._prepare_entity_from_api(raw_entity_data)
        else:
            self._prepare_entity_from_export(raw_entity_data)

    def _prepare_entity_from_export(self, raw_entity_data):
        self.user = raw_entity_data[0]
        self.description = raw_entity_data[1]
        self.date = raw_entity_data[2]
        self.project = raw_entity_data[3]
        self.start_date = raw_entity_data[4]
        self.end_date = raw_entity_data[5]
        self.duration_human_readable = raw_entity_data[6]
        self.duration = float(raw_entity_data[7])
        self.device = raw_entity_data[8]

    def _prepare_entity_from_api(self, api_data):
        self.user = api_data['user_name']
        self.description = api_data['task_name']
        start_date = api_data['start_time'].split(' ')
        end_date = api_data['end_time'].split(' ')
        self.date = start_date[0]
        self.project = api_data['project_name']
        self.start_date = start_date[1]
        self.end_date = end_date[1]
        self.duration_human_readable = api_data['length']
        self.duration = float(api_data['length'])
        self.device = api_data['edited']

    def get_user(self):
        return self.user

    def get_description(self):
        return self.description

    def get_duration(self):
        return self.duration

    def get_human_readable_duration(self):
        return self.duration_human_readable

    def get_date(self):
        return self.date

    def get_start_date(self):
        return self.start_date

    def get_project(self):
        return self.project

    def is_data_from_api(self, raw_entity_data):
        if 'id' in raw_entity_data:
            return True
        return False
