# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from unittest import mock

import pytest

from .validate_spec_url_test import make_mock_responses
from .validate_spec_url_test import read_contents
from swagger_spec_validator.common import get_uri_from_file_path
from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator12 import validate_data_type
from swagger_spec_validator.validator12 import validate_model
from swagger_spec_validator.validator12 import validate_parameter
from swagger_spec_validator.validator12 import validate_spec
from tests import TESTS_BASE_PATH


RESOURCE_LISTING_FILE = TESTS_BASE_PATH + "/data/v1.2/foo/swagger_api.json"
API_DECLARATION_FILE = TESTS_BASE_PATH + "/data/v1.2/foo/foo.json"


def get_resource_listing():
    return read_contents(RESOURCE_LISTING_FILE)


def test_http_success():
    mock_responses = make_mock_responses([API_DECLARATION_FILE])

    with mock.patch(
        "swagger_spec_validator.validator12.read_url", side_effect=mock_responses
    ) as mock_read_url:
        validate_spec(get_resource_listing(), "http://localhost/api-docs")
        mock_read_url.assert_called_once_with("http://localhost/api-docs/foo")


def test_file_uri_success():
    mock_string = "swagger_spec_validator.validator12.validate_api_declaration"
    with mock.patch(mock_string) as mock_api:
        validate_spec(
            get_resource_listing(),
            get_uri_from_file_path(RESOURCE_LISTING_FILE),
        )

        expected = read_contents(API_DECLARATION_FILE)
        mock_api.assert_called_once_with(expected)


def test_validate_parameter_type_file_in_form():
    parameter = {
        "paramType": "form",
        "name": "what",
        "type": "File",
    }
    # lack of errors is success
    validate_parameter(parameter, [])


def test_validate_parameter_type_file_in_body():
    parameter = {
        "paramType": "body",
        "name": "what",
        "type": "File",
    }
    with pytest.raises(
        SwaggerValidationError, match='Type "File" is only valid for form parameters'
    ):
        validate_parameter(parameter, [])


def test_validate_data_type_is_model():
    model_id = "MyModelId"
    model_ids = [model_id, "OtherModelId"]
    obj = {"type": model_id}
    # lack of error is success
    validate_data_type(obj, model_ids, allow_refs=False)


def test_validate_model_matches_id():
    model = {"id": "mysupermodel"}
    model_name = "mymodel"
    model_ids = ""

    with pytest.raises(
        SwaggerValidationError,
        match="model name: mymodel does not match model id: mysupermodel",
    ):
        validate_model(model, model_name, model_ids)
