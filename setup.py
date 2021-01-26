#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from os.path import abspath, dirname, join
from setuptools import setup

currdir = abspath(dirname(__file__))
with open(join(currdir, 'README.md')) as f:
    long_descr = f.read()

setup(
  name = "webgrep-tool",
  author = "Alexandre D\'Hondt",
  author_email = "alexandre.dhondt@gmail.com",
  url = "https://github.com/dhondta/webgrep",
  version = "1.14",
  license = "GPLv3",
  description = "Web page Grep-like tool with additional features like JS deobfuscation and easy extensibility",
  long_description=long_descr,
  long_description_content_type='text/markdown',
  keywords = ["grep", "webpage", "js-deobfuscator", "css-unminifier", "exif-metadata", "ocr", "steghide"],
  scripts = ["webgrep"],
  classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Topic :: Security',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
  install_requires=["bs4", "coloredlogs", "jsbeautifier", "requests"],
  python_requires = '>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,<4',
)
