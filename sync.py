#!/usr/bin/python
import argparse
from colorama import init
from termcolor import colored
from libs.time_doctor.timedoctor import TimeDoctor
from libs.time_doctor.menu import Menu as TimeDoctorMenu
from libs.jira.jira import Jira

from libs.time_doctor.connector import Connector


def print_message(message, debug=False):
    """
    Message is written to stdOut in case debug is allowed

    :param message:
    :param debug:
    :return:
    """
    if debug:
        print(message)


def main():
    _EXAMPLE_FILE = 'data/example_data.csv'
    parser = argparse.ArgumentParser(description='Sync data from TimeDoctor to Jira')
    parser.add_argument('-f', '--file',
                        help='Input source file. Exported CSV from TimeDoctor application.',
                        default=_EXAMPLE_FILE)
    parser.add_argument('-d', '--debug',
                        help='Debugging flag',
                        action='store_const',
                        const=True,
                        default=False)
    parser.add_argument('-dr', '--dry-run',
                        help='If used, data won\'t be sent to Jira',
                        action='store_const',
                        const=True,
                        default=False)
    args = parser.parse_args()
    prepared_data = False

    if (args.file and args.file != _EXAMPLE_FILE) or (args.file == _EXAMPLE_FILE and args.debug):
        print_message('[ info ] Parsing data from file', args.debug)
        td = TimeDoctor(args.file)
        prepared_data = td.get_parsed_data()
        print_message('[ info ] Data from file prpeared', args.debug)
    else:
        print_message('[ info ]: Parsing data via API', args.debug)
        td_connector = Connector()
        print_message('[ info ]: TD Connector initialized ... ', args.debug)
        td_menu = TimeDoctorMenu()
        print_message('[ info ]: TD menu initialized ...', args.debug)
        range_menu_option = td_menu.show_range_menu()
        data_to_sync = None
        if td_menu.is_range_menu_day(range_menu_option):
            print_message('[ info ]: Preparing day data ...', args.debug)
            data_to_sync = td_connector.get_user_day_worklogs()
            print_message('[ info ]: Day data prepared ...', args.debug)
        if td_menu.is_range_menu_range(range_menu_option):
            print_message('[ info ]: Preparing range data ...', args.debug)
            data_to_sync = td_connector.get_user_range_worklogs()
            print_message('[ info ]: Range data prepared', args.debug)

        print_message('[ info ]: Sync data prepared ...', args.debug)
        if data_to_sync:
            td = TimeDoctor(data_to_sync, False)
            prepared_data = td.get_parsed_data()

    print_message('[ info ]: Data for syncing prepared ...', args.debug)
    if prepared_data:
        jira = Jira(prepared_data, args.dry_run)
        print_message('[ info ]: Data for syncing prepared in Jira classes ....', args.debug)
        jira.sync_data()
        print_message('[ info ]: Data synced to Jira', args.debug)
    else:
        print_message('[ info ]: Data were not prepared. No action taken ...', args.debug)


if __name__ == '__main__':
    try:
        init()  # For colorama and windows platform
        main()
    except Exception as e:
        print(colored('\nError:\n{}\n\n'.format(str(e)), 'grey', 'on_red'))
