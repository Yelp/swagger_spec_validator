# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re

import pytest

from swagger_spec_validator.common import read_file


@pytest.fixture
def resource_listing_abspath(test_dir):
    return os.path.join(test_dir, 'data/v1.2/foo/swagger_api.json')


@pytest.fixture
def api_declaration_abspath(test_dir):
    return os.path.join(test_dir, 'data/v1.2/foo/foo.json')


@pytest.fixture
def mock_responses(test_dir, resource_listing_abspath):
    base_url = 'http://localhost/api-docs/'

    def read_url_from_file(url):
        url = re.sub(base_url + '?', '', url)
        if not url:
            return read_file(resource_listing_abspath)
        file_path = '{}{}.json'.format(os.path.join(test_dir, 'data/v1.2/foo/'), url)
        return read_file(file_path)
    return read_url_from_file


@pytest.fixture
def resource_listing_dict(resource_listing_abspath):
    return read_file(resource_listing_abspath)


@pytest.fixture
def api_declaration_dict(api_declaration_abspath):
    return read_file(api_declaration_abspath)
