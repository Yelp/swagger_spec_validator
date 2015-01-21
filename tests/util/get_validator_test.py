import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import get_validator


def test_version_missing():
    with pytest.raises(SwaggerValidationError) as excinfo:
        get_validator({}, 'http://foo.com')
    assert 'missing' in str(excinfo.value)


def test_1_dot_x_version_not_supported():
    with pytest.raises(SwaggerValidationError) as excinfo:
        get_validator({'swaggerVersion': '0.9'}, 'http://foo.com')
    assert 'not supported' in str(excinfo.value)


def test_2_dot_x_version_not_supported():
    with pytest.raises(SwaggerValidationError) as excinfo:
        get_validator({'swagger': '0.9'}, 'http://foo.com')
    assert 'not supported' in str(excinfo.value)


def test_both_swagger_1_dot_x_and_2_dot_x_version_keys_found():
    with pytest.raises(SwaggerValidationError) as excinfo:
        spec = {'swagger': '2.0', 'swaggerVersion': '1.2'}
        get_validator(spec, 'http://foo.com')
    assert 'not both' in str(excinfo.value)


def test_success():
    validator12 = get_validator({'swaggerVersion': '1.2'}, 'http://foo.com')
    validator20 = get_validator({'swagger': '2.0'}, 'http://foo.com')
    assert validator12
    assert validator20
    assert validator12 != validator20
