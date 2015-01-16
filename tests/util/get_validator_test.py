import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import get_validator


def test_swagger_version_misssing():
    with pytest.raises(SwaggerValidationError) as excinfo:
        get_validator({}, 'http://foo.com')
    assert 'missing' in str(excinfo.value)


def test_version_not_supported():
    with pytest.raises(SwaggerValidationError) as excinfo:
        get_validator({'swaggerVersion': '0.9'}, 'http://foo.com')
    assert 'not supported' in str(excinfo.value)


def test_validator_returned():
    assert get_validator({'swaggerVersion': '1.2'}, 'http://foo.com')
    assert get_validator({'swaggerVersion': '2.0'}, 'http://foo.com')
