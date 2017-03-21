import os.path
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import validate_spec_url


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert ('<urlopen error [Errno -2] Name or service not known>'
            in str(excinfo.value))


def test_success_crossref_url_yml():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    urlpath = "file://{0}".format(os.path.join(
        my_dir, "../data/v2.0/relative_ref.yml"))
    validate_spec_url(urlpath)


def test_success_crossref_url_json():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    urlpath = "file://{0}".format(os.path.join(
        my_dir, "../data/v2.0/relative_ref.json"))
    validate_spec_url(urlpath)
