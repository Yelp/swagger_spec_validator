import json

from swagger_spec_validator.validator20 import validate_spec


def test_success(petstore_contents):
    validate_spec(json.loads(petstore_contents))
