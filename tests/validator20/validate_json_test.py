import json

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_json


def test_success():
    with open("./tests/data/v2.0/petstore.json") as f:
        petstore_spec = json.load(f)
    validate_json(petstore_spec, "schemas/v2.0/schema.json")


def test_failure():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_json({}, "schemas/v2.0/schema.json")
    assert "'swagger' is a required property" in str(excinfo.value)
