# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator12 import validate_spec_url
from tests.conftest import get_url
from tests.conftest import is_urlopen_error


def test_http_success(mock_responses):
    with mock.patch(
        'swagger_spec_validator.validator12.read_url',
        side_effect=mock_responses,
    ) as mock_read_url:
        validate_spec_url('http://localhost/api-docs')

        mock_read_url.assert_has_calls([
            mock.call('http://localhost/api-docs'),
            mock.call('http://localhost/api-docs/foo'),
        ])


def test_file_uri_success(resource_listing_abspath, api_declaration_dict):
    mock_string = 'swagger_spec_validator.validator12.validate_api_declaration'
    with mock.patch(mock_string) as mock_api:
        validate_spec_url(get_url(resource_listing_abspath))

        mock_api.assert_called_once_with(api_declaration_dict)


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert is_urlopen_error(excinfo.value)
