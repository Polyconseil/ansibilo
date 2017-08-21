# -*- coding: utf-8 -*-
# Copyright (c) Polyconseil SAS. All rights reserved.
import ansibilo.plugins.filters.defaults as filters


def test_list_or_default_list():
    assert filters.list_or_default_list([1, 2, 3]) == [1, 2, 3]
    assert filters.list_or_default_list(1) == [1]
    assert filters.list_or_default_list(None) == []
    assert filters.list_or_default_list(None, default=[1]) == [1]


def test_flatten():
    assert filters.flatten([[1, 2], 3]) == [1, 2, 3]
    assert sorted(filters.flatten({'a': 1, 'b': [2, 3]})) == [1, 2, 3]
    assert filters.flatten(1) == [1]


def test_htpasswd_file_uri():
    assert filters.htpasswd_file_uri(['htpasswd:/path/']) == '/path/'
    assert filters.htpasswd_file_uri(['other:/path/']) == ''
