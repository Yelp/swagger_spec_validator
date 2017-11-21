# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import os

import pytest
from six.moves.urllib import parse as urlparse

from swagger_spec_validator.common import read_file


@pytest.fixture(scope='session')
def petstore_contents():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_dir, '../data/v2.0/petstore.json')) as f:
        return f.read()


@pytest.fixture
def petstore_dict(petstore_contents):
    return json.loads(petstore_contents)


def get_spec_json_and_url(rel_url):
    my_dir = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.realpath(os.path.join(my_dir, rel_url))
    with open(abs_path) as f:
        return json.loads(f.read()), urlparse.urljoin('file:', abs_path)


@pytest.fixture
def polymorphic_swagger2dot0_specs_dict(test_dir):
    return read_file(os.path.join(test_dir, 'data/v2.0/test_polymorphic_specs/swagger.json'))


@pytest.fixture
def petstore_swagger2dot0_specs_dict(test_dir):
    return read_file(os.path.join(test_dir, 'data/v2.0/petstore.json'))
