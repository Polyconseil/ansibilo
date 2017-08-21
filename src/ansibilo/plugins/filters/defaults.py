# -*- coding: utf-8 -*-
# Copyright (c) Polyconseil SAS. All rights reserved.
from __future__ import unicode_literals

import netaddr


def list_or_default_list(value, default=None):
    if isinstance(value, list):
        return value
    if value:
        return [value]
    else:
        return default or []


def flatten(elements):
    """Flatten a collection of collections"""
    if isinstance(elements, list):
        return [item for element in elements for item in flatten(element)]
    elif isinstance(elements, dict):
        return flatten(list(elements.values()))
    else:
        return [elements]


def string_splitter(string, seperator=' '):
    return string.split(seperator)


def htpasswd_file_uri(value):
    for item in value:
        if item.startswith('htpasswd:'):
            return item.split(':', 1)[1]
    return ''


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            # Commons
            'list_or_default_list': list_or_default_list,
            'split': string_splitter,

            # helpers
            'htpasswd_uri': htpasswd_file_uri,
            'flatten': flatten,

            # Networks
            'net2cidr': lambda x: str(netaddr.IPNetwork('{0[network]}/{0[netmask]}'.format(x))),
        }
