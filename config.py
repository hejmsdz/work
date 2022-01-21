import yaml
import os

config_yml_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.yml')

if not os.path.exists(config_yml_path):
    print(f'Config file {config_yml_path} not found.')
    print(
        f'Copy {config_yml_path}.example -> config.yml and edit it accordingly.')
    exit(1)

with open(config_yml_path) as f:
    config = yaml.load(f, yaml.Loader)

CLOCKIFY_API_KEY = config['clockify']['api_key']
CLOCKIFY_WORKSPACE_ID = config['clockify']['workspace_id']

JIRA_HOST = config['jira']['host']
JIRA_USERNAME = config['jira']['username']
JIRA_TOKEN = config['jira']['token']

TEMPO_TOKEN = config['tempo']['token']

TASK_KEYWORDS = config['options']['task_keywords']
DEFAULT_ACCOUNTS = config['options']['default_accounts']
