import operator
import re
import requests

import config


def guess_jira_id(text):
    return config.TASK_KEYWORDS.get(text)


def extract_jira_id(text):
    jira_id = re.match('[A-Z]+-\d+', text)

    if not jira_id:
        return None

    return jira_id[0]


api = requests.Session()
api.headers.update({
    'X-Api-Key': config.CLOCKIFY_API_KEY
})
base_url = f'https://reports.api.clockify.me/v1/workspaces/{config.CLOCKIFY_WORKSPACE_ID}'


def get_clockify_report(date):
    response = api.post(
        f'{base_url}/reports/summary', json={
            'dateRangeStart': f'{date}T00:00:00Z',
            'dateRangeEnd': f'{date}T23:59:59Z',
            'summaryFilter': {
                'groups': ['USER', 'TIMEENTRY'],
                'sortColumn': 'DURATION',
            },
            'sortOrder': 'DESCENDING',
        })

    report = response.json()

    if not report['groupOne']:
        return []

    entries = sorted(report['groupOne'][0]['children'],
                     key=operator.itemgetter('duration'), reverse=True)

    results = []
    for entry in entries:
        name = entry['name']
        jira_id = extract_jira_id(name) or guess_jira_id(name)
        details = name.replace(jira_id, '').strip() if jira_id else name
        duration = entry['duration']

        results.append({
            'jira_id': jira_id,
            'details': details,
            'duration': duration,
        })

    return results
