import pprint
import sys
import re
import datetime
import config
from requests.exceptions import RequestException
from clockify import get_clockify_report
from jira import get_current_user, get_jira_ticket
from tempo import get_tempo_worklogs, get_tempo_accounts_for_project, create_tempo_worklog


def seconds_to_hms(seconds):
    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    return hours, minutes, seconds


def format_hms(hms):
    return '{:02d}:{:02d}:{:02d}'.format(*hms)


def resolve_date(date):
    if date == 'today':
        return str(datetime.date.today())
    if date == 'yesterday':
        return str(datetime.date.today() - datetime.timedelta(days=1))

    if not re.match(r'\d{4}-\d{2}-\d{2}', date):
        print('Expected YYYY-MM-DD, "yesterday" or "today" as date argument!')
        exit(1)

    return date


def get_all_accounts_by_project(report):
    projects = set()
    accounts_by_project = dict()
    for entry in report:
        if entry['jira_id']:
            projects.add(entry['jira_id'].split('-')[0])

    for project in projects:
        accounts_by_project[project] = get_tempo_accounts_for_project(project)

    return accounts_by_project


def select_account(jira_id, accounts_by_project):
    project = jira_id.split('-')[0]
    accounts = accounts_by_project[project]
    if len(accounts) == 1:
        return next(iter(accounts.keys()))

    if project in config.DEFAULT_ACCOUNTS:
        return config.DEFAULT_ACCOUNTS[project]

    print('choose account:')
    pprint.pp(accounts)
    return input()


def main():
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} [date]')
        exit(1)

    date = resolve_date(sys.argv[1])

    try:
        jira_user = get_current_user()
    except RequestException as e:
        print('Request to Jira API failed. Did you configure your jira.host, jira.username and jira.token?')
        print(e)
        exit(1)

    try:
        report = get_clockify_report(date)
    except RequestException as e:
        print('Request to Clockify API failed. Did you configure your clockify.api_key and clockify.workspace_id?')
        print(e)
        exit(1)

    if not report:
        print(f'No time Clockify entries found for {date}.')
        exit(0)

    try:
        tempo_logs = get_tempo_worklogs(date)
    except RequestException as e:
        print('Request to Tempo API failed. Did you configure your tempo.token?')
        print(e)
        exit(1)

    accounts_by_project = get_all_accounts_by_project(report)

    should_post_to_tempo = tempo_logs['metadata']['count'] == 0

    if not should_post_to_tempo:
        print(
            f'You already have worklogs for {date}. No entries will be posted to Tempo.')

    imaginary_starting_time = 8 * 3600
    for entry in report:
        summary = get_jira_ticket(entry['jira_id'])[
            'fields']['summary'] if entry['jira_id'] else None

        full_entry = {
            **entry,
            'summary': summary,
            'duration_hms': format_hms(seconds_to_hms(entry['duration']))
        }

        pprint.pp(full_entry)

        if should_post_to_tempo:
            create_tempo_worklog(
                date=date,
                jira_id=entry['jira_id'],
                duration=entry['duration'],
                start_time=format_hms(seconds_to_hms(imaginary_starting_time)),
                details=entry['details'],
                user_id=jira_user['accountId'],
                account=select_account(entry['jira_id'], accounts_by_project)
            )

        imaginary_starting_time += entry['duration']


main()
