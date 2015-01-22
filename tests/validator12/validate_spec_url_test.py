import json

import mock
import StringIO

from swagger_spec_validator.validator12 import validate_spec_url


RESOURCE_LISTING = {
    "swaggerVersion": "1.2",
    "apis": [
        {
            "path": "/foo",
            "description": "Some description"
        }
    ]
}


API_DECLARATION = {
    "swaggerVersion": "1.2",
    "basePath": "http://localhost",
    "apis": [
        {
            "path": "/foo",
            "operations": [
                {
                    "method": "GET",
                    "nickname": "foo",
                    "parameters": [
                        {
                            "paramType": "query",
                            "name": "name",
                            "type": "string"
                        }
                    ],
                    "type": "string"
                }
            ]
        }
    ]
}


def make_mock_responses(mock_responses):
    return [
        StringIO.StringIO(json.dumps(mock_response))
        for mock_response in mock_responses
    ]


def test_success():
    mock_responses = make_mock_responses([
        RESOURCE_LISTING,  # ingest
        API_DECLARATION])  # ingest

    with mock.patch('swagger_spec_validator.util.urllib2.urlopen',
                    side_effect=mock_responses) as mock_urlopen:
        validate_spec_url('http://localhost/api-docs')

        mock_urlopen.assert_has_calls([
            mock.call('http://localhost/api-docs', timeout=1),
            mock.call('http://localhost/api-docs/foo', timeout=1),
        ])
