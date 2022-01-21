import requests
import config

api = requests.Session()
api.auth = (config.JIRA_USERNAME, config.JIRA_TOKEN)
base_url = f'https://{config.JIRA_HOST}/rest/api/2'


def get_current_user():
    response = api.get(f'{base_url}/myself')
    return response.json()


def get_jira_ticket(jira_id):
    response = api.get(f'{base_url}/issue/{jira_id}')
    return response.json()
