import json
import mock
import os
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec_url


def test_success(petstore_contents):
    with mock.patch(
            'swagger_spec_validator.validator20.load_json',
            return_value=json.loads(petstore_contents)) as mock_load_json:
        validate_spec_url('http://localhost/api-docs')
        mock_load_json.assert_called_once_with('http://localhost/api-docs')


def test_success_crossref_url():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    urlpath = "file://{0}".format(os.path.join(
        my_dir, "../data/v2.0/relative_ref.json"))
    validate_spec_url(urlpath)


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert ('<urlopen error [Errno -2] Name or service not known>'
            in str(excinfo.value))
