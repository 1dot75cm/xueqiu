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
from setuptools.command.install import install
from subprocess import getoutput
import sys
import re


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v']
        self.test_suite = True

    def run_tests(self):
        import pytest
        err_code = pytest.main(self.test_args)
        sys.exit(err_code)


class PostInstall(install):
    """run post install."""
    pkgs = ' git+https://github.com/1dot75cm/browsercookie@master'
    def run(self):
        install.run(self)
        print(getoutput('pip install'+self.pkgs))


def gendeps(filename):
    with open(filename, 'r') as f:
        return re.split("\n", f.read())


with open('xueqiu/__init__.py', 'rt', encoding='utf8') as f:
    xueqiu = dict(re.findall(r'__(.*?)__ = "(.*?)"', f.read()))


setup(
    name=xueqiu['pkgname'],
    version=xueqiu['version'],
    license=xueqiu['license'],
    url=xueqiu['url'],
    author=xueqiu['author'],
    author_email=xueqiu['email'],
    description=xueqiu['descript'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests']),
    package_dir={'xueqiu': 'xueqiu'},
    include_package_data=True,
    platforms='any',
    install_requires=gendeps('requirements.txt'),
    tests_require=gendeps('requirements-test.txt'),
    test_suite="tests",
    cmdclass={'install': PostInstall, 'test': PyTest},
    keywords=['xueqiu', 'snowball', 'stock', 'api', 'api client', 'wrappers'],
    # https://pypi.org/classifiers/
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