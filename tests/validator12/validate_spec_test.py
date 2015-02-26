import os

import mock

from .validate_spec_url_test import make_mock_responses, read_contents
from swagger_spec_validator.validator12 import validate_spec


RESOURCE_LISTING_FILE = os.path.abspath('tests/data/v1.2/foo/swagger_api.json')
API_DECLARATION_FILE = os.path.abspath('tests/data/v1.2/foo/foo.json')


def get_resource_listing():
    return read_contents(RESOURCE_LISTING_FILE)


def test_http_success():
    mock_responses = make_mock_responses([API_DECLARATION_FILE])

    with mock.patch('swagger_spec_validator.validator12.load_json',
                    side_effect=mock_responses) as mock_load_json:
        validate_spec(get_resource_listing(), 'http://localhost/api-docs')

        mock_load_json.assert_called_once_with('http://localhost/api-docs/foo')


def test_file_uri_success():
    mock_string = 'swagger_spec_validator.validator12.validate_api_declaration'
    with mock.patch(mock_string) as mock_api:
        validate_spec(get_resource_listing(),
                      'file://{0}'.format(RESOURCE_LISTING_FILE))

        expected = read_contents(API_DECLARATION_FILE)
        mock_api.assert_called_once_with(expected)
