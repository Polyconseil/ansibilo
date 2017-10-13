# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os
import os.path

import humanize
import requests

from ansible.constants import config
from ansible.plugins.callback import CallbackBase


DOCUMENTATION = '''
    callback: vaulted-slack
    callback_type: notification
    short_description: Sends play result to a Slack channel
    description:
        - This is an ansible callback plugin that sends play results to a Slack channel
    options:
      token:
        required: True
        description: Slack Webhook token
        env:
          - name: VAULTED_SLACK_TOKEN
        ini:
          - section: vaulted-slack
            key: token
'''


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'vaulted_slack'
    CALLBACK_NEEDS_WHITELIST = True

    SLACK_HOOK_FORMAT = 'https://hooks.slack.com/services/{token}'

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._loader = None
        self.start_ts = None
        self.playbook_name = None
        self.user = None
        self.skip_slack = False

    @property
    def slack_hook_url(self):
        if not self._loader:
            return

        slack_token_key_uri = config.get_config_value('token', plugin_type='callback', plugin_name='vaulted_slack')
        file_path, name = slack_token_key_uri.split('#')
        path = name.split('.')

        data = self._loader.load_from_file(file_path)
        for item in path[:-1]:
            data = data.get(item, {})
        token = data[path[-1]]

        return self.SLACK_HOOK_FORMAT.format(token=token)

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
        self._loader = playbook.get_loader()
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
