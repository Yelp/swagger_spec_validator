import json
import os
from unittest import mock

import pytest

from swagger_spec_validator.common import get_uri_from_file_path
from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.common import SwaggerValidationWarning
from swagger_spec_validator.validator20 import validate_spec_url
from tests.conftest import is_urlopen_error


def test_success(petstore_contents):
    with mock.patch(
        "swagger_spec_validator.validator20.read_url",
        return_value=json.loads(petstore_contents),
    ) as mock_read_url:
        validate_spec_url("http://localhost/api-docs")
        mock_read_url.assert_called_once_with("http://localhost/api-docs")


def test_success_crossref_url_yaml():
    urlpath = get_uri_from_file_path(os.path.abspath("./tests/data/v2.0/minimal.yaml"))
    validate_spec_url(urlpath)


def test_success_crossref_url_json():
    urlpath = get_uri_from_file_path(
        os.path.abspath("./tests/data/v2.0/relative_ref.json")
    )
    validate_spec_url(urlpath)


def test_complicated_refs_json():
    urlpath = get_uri_from_file_path(
        os.path.abspath("./tests/data/v2.0/test_complicated_refs/swagger.json")
    )
    validate_spec_url(urlpath)


def test_specs_with_empty_reference():
    with pytest.warns(SwaggerValidationWarning) as warninfo:
        validate_spec_url(
            get_uri_from_file_path(
                os.path.abspath(
                    "./tests/data/v2.0/invalid_swagger_spec_because_empty_reference.yaml"
                ),
            ),
        )

    assert (
        "Identified $ref with None value. This is usually an error, although technically it might be allowed. "
        "(path: #/definitions/model1/x-extends)" == str(warninfo.list[0].message)
    )


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url("http://foo")
    assert is_urlopen_error(excinfo.value)
