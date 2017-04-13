# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os
import os.path

import humanize
import requests

import ansible.constants as C
from ansible.cli import CLI
from ansible.parsing import dataloader
from ansible.plugins.callback import CallbackBase


def var_uri_value(uri):
    """Read a value from the ansible vault.

    Args:
        - uri: str, URI formatted key to read in the vault (e.g.: path/to/vault.yml#section.key)

    Returns: the value kept in the vault.
    """
    if '#' not in uri:
        return None

    file_path, name = uri.split('#')
    path = name.split('.')

    loader = dataloader.DataLoader()
    b_vault_pass = CLI.read_vault_password_file(C.DEFAULT_VAULT_PASSWORD_FILE, loader=loader)
    loader.set_vault_password(b_vault_pass)
    data = loader.load_from_file(file_path)

    for item in path[:-1]:
        data = data.get(item, {})
    return data[path[-1]]


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'vaulted_slack'
    CALLBACK_NEEDS_WHITELIST = True

    SLACK_HOOK_FORMAT = 'https://hooks.slack.com/services/{token}'

    def __init__(self):
        super(CallbackModule, self).__init__()

        slack_token_key_uri = C.get_config(C.p, 'vaulted-slack', 'token-key', None, 'slack_token')
        self.token = var_uri_value(slack_token_key_uri)

        self.slack_hook_url = self.SLACK_HOOK_FORMAT.format(token=self.token)
        self.start_ts = None
        self.playbook_name = None
        self.user = None
        self.skip_slack = False

    def v2_runner_on_ok(self, res):
        try:
            facts = res._result['ansible_facts']
            self.user = (
                self.user
                or facts['ansible_env'].get('SUDO_USER')
                or facts['ansible_user_id']
            )
        except KeyError:
            pass

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)
        self.start_ts = datetime.now()

    def v2_runner_on_failed(self, result, ignore_errors=False):
        # If we failed to become sudoer, don't post to slack
        self.skip_slack = result._result['msg'] == 'Incorrect sudo password'

    def v2_playbook_on_stats(self, stats):
        if stats.failures and stats.ok:
            color = 'warning'
        elif not stats.failures:
            color = 'good'
        else:
            color = 'danger'
        end_ts = datetime.now()
        delta = humanize.naturaldelta(end_ts - self.start_ts) if self.start_ts else 'unknown'
        title = "Playbook {name} run in {time}".format(name=self.playbook_name, time=delta)

        hosts = stats.processed.keys()
        payload = {'attachments': [
            {
                'title': title,
                'color': color,
                'author_name': self.user,
                'fields': [{
                    'title': '',
                    'value': "{emoji} {host}".format(
                        emoji=':boom:' if host in stats.failures else ':ok_hand:',
                        host=host,
                    ),
                    'short': True,
                } for host in hosts],
                # For IRC users
                'fallback': '\n'.join([title, "by {0}".format(self.user)] + [
                    ' - {host}: {status}'.format(
                        host=host,
                        status='failed' if host in stats.failures else 'ok',
                    )
                    for host in hosts
                ]),
            }
        ]}

        if os.environ.get('VAGRANT_EXECUTABLE'):  # Do not post on slack when playbook is run by Vagrant
            print('{delimiter}POST {url}\n{payload}{delimiter}'.format(
                url=self.slack_hook_url,
                payload=json.dumps(payload, indent=True),
                delimiter='\n' + '-' * 30 + ' slack ' + '-' * 30 + '\n',
            ))
        elif not self.skip_slack:
            requests.post(self.slack_hook_url, data=json.dumps(payload))
