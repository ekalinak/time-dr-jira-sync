from tabulate import tabulate
from .connector import Connector


class Report:
    def __init__(self):
        self._connector = Connector()
        self._flags = {
            'day_data_processed': False
        }

    def get_day_report(self):
        day_data = self._connector.get_user_day_worklogs()
        day_data_formatted = day_data
        if not self._flags['day_data_processed']:
            day_data_formatted = list(map(lambda elem: self._convert_time(elem), day_data))
            day_data_formatted.sort(key=lambda x: x['id'])
            self._flags['day_data_processed'] = True
        print(tabulate(day_data_formatted, tablefmt='fancy_grid', headers='keys'))

    def _convert_time(self, worklog):
        worklog['length'] = self._display_time(int(worklog['length']))
        return worklog

    def _display_time(self, seconds, granularity=2):
        intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),  # 60 * 60 * 24
            ('hours', 3600),  # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []
        seconds = int(seconds)

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])
