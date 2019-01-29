#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
xueqiu.api
~~~~~~~~~~

This module implements a humanize XueQiu API wrappers.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import re
import xueqiu


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v']
        self.test_suite = True

    def run_tests(self):
        import pytest
        err_code = pytest.main(self.test_args)
        sys.exit(err_code)


def gendeps(filename):
    with open(filename, 'r') as f:
        return re.split("\n", f.read())


setup(
    name=xueqiu.__pkgname__,
    version=xueqiu.__version__,
    license=xueqiu.__license__,
    url=xueqiu.__url__,
    author=xueqiu.__author__,
    author_email=xueqiu.__email__,
    description=xueqiu.__descript__,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests']),
    package_dir={'xueqiu': 'xueqiu'},
    include_package_data=True,
    platforms='any',
    install_requires=gendeps('requirements.txt'),
    tests_require=gendeps('requirements-test.txt'),
    test_suite="tests",
    cmdclass={'test': PyTest},
    keywords=['xueqiu', 'snowball', 'stock', 'api', 'api client', 'wrappers'],
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities'
    ]
)