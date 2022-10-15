# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest


def is_urlopen_error(exception):
    return any(
        urlopen_error_str in str(exception)
        for urlopen_error_str in {
            "<urlopen error [Errno -2] Name or service not known>",
            "<urlopen error [Errno -3] Temporary failure in name resolution>",
            "<urlopen error [Errno 8] nodename nor servname provided, or not known",
            "<urlopen error [Errno -5] No address associated with hostname>",
            "<urlopen error [Errno 11001] getaddrinfo failed>",
        }
    )


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
