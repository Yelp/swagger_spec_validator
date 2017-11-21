# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest
from six.moves.urllib.parse import urljoin


def is_urlopen_error(exception):
    return '<urlopen error [Errno -2] Name or service not known>' in str(exception) or \
           '<urlopen error [Errno 8] nodename nor servname provided, or not known' in str(exception) or \
           '<urlopen error [Errno -5] No address associated with hostname>' in str(exception)


@pytest.fixture
def test_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_url(absolute_path):
    return urljoin('file:', absolute_path)
