import json

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator12 import validate_json


def test_success():
    with open("./tests/data/v1.2/foo/swagger_api.json") as f:
        resource_listing = json.load(f)
    validate_json(resource_listing, "schemas/v1.2/resourceListing.json")

    with open("./tests/data/v1.2/foo/foo.json") as f:
        api_declaration = json.load(f)
    validate_json(api_declaration, "schemas/v1.2/apiDeclaration.json")


def test_failure():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_json({}, "schemas/v1.2/apiDeclaration.json")
    assert "'swaggerVersion' is a required property" in str(excinfo.value)
