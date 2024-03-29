from unittest import mock

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import validate_spec_url
from tests.conftest import is_urlopen_error


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url("http://foo")
    assert is_urlopen_error(excinfo.value)


@mock.patch("swagger_spec_validator.util.read_url")
@mock.patch("swagger_spec_validator.util.get_validator")
def test_validate_spec_url_success(mock_get_validator, mock_read_url):
    spec_url = mock.Mock()
    validate_spec_url(spec_url)
    mock_read_url.assert_called_once_with(spec_url)
    mock_get_validator.assert_called_once_with(mock_read_url.return_value, spec_url)
