#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def read(file_path):
    with open(file_path) as fp:
        return fp.read()


setup(
    name='ansibilo',
    version='0.1.1',
    description="Set of tools for Ansible",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Systems Administration',
    ],
    keywords=['ansible', 'tools'],
    author='Polyconseil',
    author_email='opensource+ansibilo@polyconseil.fr',
    url='https://github.com/Polyconseil/ansibilo/',
    license='BSD',
    packages=find_packages(where='src') + [
        'ansible.modules.ansibilo',
        'ansible.plugins.callback.ansibilo',
        'ansible.plugins.filter.ansibilo',
    ],
    package_dir={
        '': str('src'),
        'ansible.modules.ansibilo': str('src/ansibilo/modules'),
        'ansible.plugins.callback.ansibilo': str('src/ansibilo/plugins/callbacks'),
        'ansible.plugins.filter.ansibilo': str('src/ansibilo/plugins/filters'),
    },
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'setuptools',
    ],
    install_requires=[
        'ansible',
        'click',
        'graphviz',
        'humanize',
        'netaddr',
    ],
    extras_require={
      'sphinx': [
          'sphinx',
      ],
    },
    entry_points={
        'console_scripts': (
            'ansibilo = ansibilo.__main__:main',
        ),
    },
)
