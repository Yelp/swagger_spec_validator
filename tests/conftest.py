import os

import pytest
from six.moves.urllib.parse import urljoin


@pytest.fixture
def test_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_url(absolute_path):
    return urljoin('file:', absolute_path)
