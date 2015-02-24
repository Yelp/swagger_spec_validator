import mock
import pytest
import StringIO

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec_url


def test_success(petstore_contents):
    mock_responses = [StringIO.StringIO(petstore_contents)]
    with mock.patch(
            'swagger_spec_validator.util.urllib2.urlopen',
            side_effect=mock_responses) as mock_urlopen:
        validate_spec_url('http://localhost/api-docs')
        mock_urlopen.assert_has_calls([
            mock.call('http://localhost/api-docs', timeout=1)])


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert ('<urlopen error [Errno -2] Name or service not known>'
            in str(excinfo.value))
