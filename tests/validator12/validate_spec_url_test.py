import json
import os

import mock
import pytest
import StringIO

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator12 import validate_spec_url


RESOURCE_LISTING_FILE = os.path.abspath('tests/data/v1.2/foo/swagger_api.json')
API_DECLARATION_FILE = os.path.abspath('tests/data/v1.2/foo/foo.json')


def read_contents(file_name):
    with open(file_name) as f:
        return StringIO.StringIO(f.read())


def make_mock_responses(file_names):
    return [read_contents(file_name) for file_name in file_names]


def test_http_success():
    mock_responses = make_mock_responses([RESOURCE_LISTING_FILE,
                                          API_DECLARATION_FILE])

    with mock.patch('swagger_spec_validator.util.urllib2.urlopen',
                    side_effect=mock_responses) as mock_urlopen:
        validate_spec_url('http://localhost/api-docs')

        mock_urlopen.assert_has_calls([
            mock.call('http://localhost/api-docs', timeout=1),
            mock.call('http://localhost/api-docs/foo', timeout=1),
        ])


def test_file_uri_success():
    mock_string = 'swagger_spec_validator.validator12.validate_api_declaration'
    with mock.patch(mock_string) as mock_api:
        validate_spec_url('file://{0}'.format(RESOURCE_LISTING_FILE))

        expected = json.load(read_contents(API_DECLARATION_FILE))
        mock_api.assert_called_once_with(expected)


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert ('<urlopen error [Errno -2] Name or service not known>'
            in str(excinfo.value))
