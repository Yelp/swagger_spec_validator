import mock
import os
import StringIO

from swagger_spec_validator.validator20 import validate_spec_url


def test_success():
    my_dir = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(my_dir, '../data/v2.0/petstore.json')) as f:
        petstore_contents = f.read()

    mock_responses = [StringIO.StringIO(petstore_contents)]

    with mock.patch(
            'swagger_spec_validator.util.urllib2.urlopen',
            side_effect=mock_responses) as mock_urlopen:

        validate_spec_url('http://localhost/api-docs')

        mock_urlopen.assert_has_calls([
            mock.call('http://localhost/api-docs', timeout=1),
        ])
