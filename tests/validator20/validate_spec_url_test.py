# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import mock
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec_url
from tests.conftest import get_url
from tests.conftest import is_urlopen_error


def test_success(petstore_swagger2dot0_specs_dict):
    with mock.patch(
        'swagger_spec_validator.validator20.read_url',
        return_value=petstore_swagger2dot0_specs_dict,
    ) as mock_read_url:
        validate_spec_url('http://localhost/swagger.json')
        mock_read_url.assert_called_once_with('http://localhost/swagger.json')


def test_success_crossref_url_yaml(test_dir):
    validate_spec_url(get_url(os.path.join(test_dir, 'data/v2.0/minimal.yaml')))


def test_success_crossref_url_json(test_dir):
    validate_spec_url(get_url(os.path.join(test_dir, 'data/v2.0/relative_ref.json')))


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert is_urlopen_error(excinfo.value)
