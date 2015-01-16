import json
import os
import pytest

from jsonschema.exceptions import ValidationError

from swagger_spec_validator.common import validate_json


def test_success():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_dir, '../data/v2.0/petstore.json')) as petstore_file:
        petstore_spec = json.load(petstore_file)
    validate_json(petstore_spec, 'schemas/v2.0/schema.json')


def test_failure():
    with pytest.raises(ValidationError):
        validate_json({}, 'schemas/v2.0/schema.json')
