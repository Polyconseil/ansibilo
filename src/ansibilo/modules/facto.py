#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) Polyconseil SAS. All rights reserved.
"""
This module allow to remotely generate secrets and port allocations

Allowed kinds are:

- ``secret``
- ``tcp-port``
- ``udp-port``

usage::

    - name: Remotely generated secret
      facto:
        key: my-secret
        kind: secret
        fact: my_secret

    - name: Use secret
      copy:
        content: "{{ my_secret }}"
        dest: /my/secret/path

"""
from __future__ import absolute_import, division, print_function, unicode_literals
import base64
import json
import math
import os
import os.path
import random
import socket
import stat

from ansible.module_utils.basic import AnsibleModule

FACT_DIRECTORY = '/etc/ansible/facts.d'
PORT_RANGE = (10000, 30000)


def makedirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def read(filename):
    """
    Read JSON data from file.

    Args:
        filename (str): file path
    """
    if not os.path.exists(filename):
        return {}
    with open(filename) as fp:
        return json.load(fp)


def write(filename, data, undisclosed=False):
    """
    Write JSON data to (owner only readable) file.

    This will also create missing directories.

    Args:
        filename (str): file path
        data (str): data to write
        undisclosed (bool): whether data should be owner only readable
    """
    makedirs(os.path.dirname(filename))
    with open(filename, 'w') as fp:
        if undisclosed:
            os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)
        json.dump(data, fp)


def generate_secret(bits):
    """
    Generate a secret with at least `bits` bits of entropy.

    The secret is encoded in base 64, so its length is a little more that `bits` / 8. bytes.

    Args:
        bits (int): minimal bits of entropy needed

    Return:
        str: secret with at least `bits` bits of entropy

    """
    return base64.b64encode(os.urandom(int(math.ceil(bits / 8.))))


def is_iana_reserved_port(port, protocol):
    """
    Check whether the port is reserved by IANA
    Args:
        port (int): port
        protocol (str): application protocol (tcp or udp)
    Return:
        bool: whether the port is reserved by IANA
    """
    try:
        socket.getservbyport(port, protocol)
        return True
    except socket.error:
        return False


def is_unused_port(port, protocol):
    """
    Check whether the port is unused
    Args:
        port (int): port
        protocol (str): application protocol (tcp or udp)
    Return:
        bool: whether the port is unused
    """
    protocols = {
        'udp': socket.SOCK_DGRAM,
        'tcp': socket.SOCK_STREAM,
    }
    sock = socket.socket(family=socket.AF_INET, type=protocols[protocol])
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except socket.error:
        return False


def get_unused_port(protocol, already_reserved_ports):
    """
    Get an unused port
    Args:
        protocol (str): application protocol (tcp or udp)
        already_reserved_ports (dict): list of known used ports
    Return:
        int: an unused port
    """
    port = random.randint(*PORT_RANGE)

    if (
        port not in already_reserved_ports.values()
        and not is_iana_reserved_port(port, protocol)
        and is_unused_port(port, protocol)
    ):
        return port

    return get_unused_port(protocol, already_reserved_ports)


def get_or_create(kind, key, db, dry_run=False, **kwargs):
    kinds = {
        'secret': lambda: (True, generate_secret(256)),
        'tcp-port': lambda: (False, get_unused_port('tcp', data)),
        'udp-port': lambda: (False, get_unused_port('udp', data)),
    }

    filename = os.path.join(db, 'facto.{}s.fact'.format(kind))
    data = read(filename)
    if key in data:
        return data[key], False

    undisclosed, data[key] = kinds[kind]()
    if not dry_run:
        write(filename, data, undisclosed)
    return data[key], True


def main():
    module = AnsibleModule(
        argument_spec={
            'key': {'required': True},
            'kind': {'required': True, 'choices': ('secret', 'tcp-port', 'udp-port')},
            'db': {'default': FACT_DIRECTORY},
            'fact': {'required': False},
        },
        supports_check_mode=True,
    )

    value, created = get_or_create(dry_run=module.check_mode, **module.params)
    facts = {module.params['fact']: value} if module.params['fact'] else {}
    return module.exit_json(
        changed=created,
        value=value,
        ansible_facts=facts,
    )


# Ansible idiomatic
if __name__ == '__main__':
    main()
