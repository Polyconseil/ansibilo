# -*- coding: utf-8 -*-
from __future__ import print_function
import json

import ansible.utils.color as ansible_color
import ansible.plugins.callback as ansible_callback


def split_output(key, value):
    if key in ('stdout', 'stderr'):
        return str(value).split('\n')
    return value


class CallbackModule(ansible_callback.CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_NAME = 'pretty_print_result'
    CALLBACK_NEEDS_WHITELIST = True

    def _pretty_print(self, data, color='normal'):
        if self._display.verbosity <= 1:  # Do not use multi-line output when verbosity is less than 2
            return

        formatted_data = {k: split_output(k, v) for k, v in data.items()} if isinstance(data, dict) else data
        formatted_data = json.dumps(formatted_data, sort_keys=True, indent=2, separators=(',', ': '))
        formatted_data = ansible_color.stringc(formatted_data, color)

        print(formatted_data)

    def runner_on_failed(self, host, data, ignore_errors=False):
        self._pretty_print(data, color='red')

    def runner_on_ok(self, host, data):
        self._pretty_print(data, color='yellow' if data.get('changed', False) else 'green')

    def runner_on_unreachable(self, host, data):
        self._pretty_print(data)

    def runner_on_async_poll(self, host, data, jid, clock):
        self._pretty_print(data)

    def runner_on_async_ok(self, host, data, jid):
        self._pretty_print(data)

    def runner_on_async_failed(self, host, data, jid):
        self._pretty_print(data)
