import requests

import config

api = requests.Session()
api.headers.update({
    'Authorization': f'Bearer {config.TEMPO_TOKEN}'
})
base_url = 'https://api.tempo.io/core/3'


def get_tempo_worklogs(date):
    response = api.get(
        f'{base_url}/worklogs',
        params={'from': date, 'to': date},
    )

    data = response.json()

    return data


def get_tempo_accounts_for_project(project_key):
    response = api.get(
        f'{base_url}/account-links/project/{project_key}',
    )

    data = response.json()
    results = {}

    for account in data['results']:
        account_id = account['account']['key']
        name = account['account']['name']
        results[account_id] = name

    return results


def create_tempo_worklog(*, date, jira_id, duration, start_time, details, user_id, account):
    response = api.post(
        f'{base_url}/worklogs',
        json={
            'issueKey': jira_id,
            'timeSpentSeconds': duration,
            'startDate': date,
            'startTime': start_time,
            'description': details,
            'authorAccountId': user_id,
            'attributes': [
                {
                    'key': '_Account_',
                    'value': account,
                },
            ],
        },
    )

    data = response.json()

    return data
