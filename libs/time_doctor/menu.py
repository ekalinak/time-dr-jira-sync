from .report import Report
import sys


class Menu:
    def __init__(self):
        self._RANGE_MENU_DAY = 1
        self._RANGE_MENU_RANGE = 2
        self._RANGE_MENU_EXIT = 3

    def show_report_menu(self):
        """
        TODO: Features for future

        :return: void
        """
        report = Report()
        print('Time doctor menu')
        print('================')
        option = '0'

        while option != '5':
            if option == '1':
                report.get_day_report()
            if option == '2':
                break
            if option == '3':
                break
            if option == '4':
                break

            option = input('\nSelect option: \n'
                           '  1) Detailed Day Report\n'
                           '  2) Summary Date Report\n'
                           '  3) Detailed Date range report\n'
                           '  4) Summary Date Range Report\n'
                           '  5) Exit\n\n'
                           'Your choice: ')

    def show_range_menu(self):
        print('Please choose date range method:')
        print('================================')
        option = input('\n  '
                       '{}) One day\n  '
                       '{}) Date range\n  '
                       '{}) Exit\n\n'
                       'Your answer: '.format(self._RANGE_MENU_DAY, self._RANGE_MENU_RANGE, self._RANGE_MENU_EXIT))
        if int(option) == self._RANGE_MENU_EXIT:
            sys.exit('Exiting ...')

        while int(option) not in [self._RANGE_MENU_DAY, self._RANGE_MENU_RANGE]:
            option = input('You have not entered possible values. Try again: ')

        return int(option)

    def is_range_menu_day(self, test_value):
        return test_value == self._RANGE_MENU_DAY

    def is_range_menu_range(self, test_value):
        return test_value == self._RANGE_MENU_RANGE
