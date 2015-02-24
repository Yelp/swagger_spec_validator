import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import validate_spec_url


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert ('<urlopen error [Errno -2] Name or service not known>'
            in str(excinfo.value))
