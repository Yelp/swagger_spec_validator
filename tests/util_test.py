import json

import mock
import StringIO

from swagger_spec_validator import validate_resource_listing_url


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


def test_http():
    mock_responses = make_mock_responses([RESOURCE_LISTING, API_DECLARATION])

    with mock.patch('swagger_spec_validator.util.urllib2.urlopen',
                    side_effect=mock_responses) as mock_urlopen:
        validate_resource_listing_url('http://localhost')

        mock_urlopen.assert_has_calls([
            mock.call('http://localhost', timeout=1),
            mock.call('http://localhost/foo', timeout=1),
        ])
