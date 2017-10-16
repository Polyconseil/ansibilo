import importlib
import os.path
import pkgutil
import sys

import pkg_resources
import pytest


def is_distribution_editable(name):
    """Is distribution an editable install?"""
    distribution = pkg_resources.get_distribution(name)
    return any(
        os.path.isfile(
            os.path.join(location, distribution.project_name + '.egg-link'),
        )
        for location in sys.path
    )


skip_if_editable = pytest.mark.skipif(
    is_distribution_editable('ansibilo'),
    reason='Ansibilo is an editable installation (so Ansible modules are not installed)',
)


def sub_module_iterator(module_name):
    directory = os.path.join(
        os.path.dirname(__file__),
        '../src/',
        module_name.replace('.', '/')
    )
    return pkgutil.iter_modules([directory])


def try_import(module_name):
    try:
        return importlib.import_module(module_name)
    except (ImportError, ModuleNotFoundError):
        return None
