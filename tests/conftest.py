# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import pathname2url


def is_urlopen_error(exception):
    return '<urlopen error [Errno -2] Name or service not known>' in str(exception) or \
           '<urlopen error [Errno 8] nodename nor servname provided, or not known' in str(exception) or \
           '<urlopen error [Errno -5] No address associated with hostname>' in str(exception)


@pytest.fixture(autouse=True)
def change_dir():
    """
    Change the base directory to git root directory such that tests does not need to
    generate the absolute path for the data files.
    A relative path from git top-level directory will work as well
    """
    current_directory = os.path.abspath(os.curdir)
    try:
        os.chdir(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        yield
    finally:
        os.chdir(current_directory)


def get_uri_from_file_path(file_path):
    return urljoin('file://', pathname2url(file_path))
