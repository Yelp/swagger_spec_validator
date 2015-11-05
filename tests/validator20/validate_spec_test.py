import json
import os
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec


@pytest.fixture
def minimal_swagger_dict():
    """Return minimal dict that respresents a swagger spec - useful as a base
    template.
    """
    return {
        'swagger': '2.0',
        'info': {
            'title': 'Test',
            'version': '1.0',
        },
        'paths': {
        },
        'definitions': {
        },
    }


def test_success(petstore_contents):
    validate_spec(json.loads(petstore_contents))


def test_definitons_not_present_success(minimal_swagger_dict):
    del minimal_swagger_dict['definitions']
    validate_spec(minimal_swagger_dict)


def test_empty_definitions_success(minimal_swagger_dict):
    validate_spec(minimal_swagger_dict)


def test_api_parameters_as_refs():
    # Verify issue #29 - instragram.json comes from:
    #
    # http://editor.swagger.io/#/
    #    -> File
    #       -> Open Example...
    #          -> instagram.yaml
    #
    # and then export it to a json file.
    my_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_dir, '../data/v2.0/instagram.json')) as f:
        validate_spec(json.loads(f.read()))


def test_fails_on_invalid_external_ref():
    # The external ref in petstore.json is valid.
    # The contents of the external ref (pet.json#/getall) is not - the 'name'
    # key in the parameter is missing.
    my_dir = os.path.abspath(os.path.dirname(__file__))

    petstore_path = os.path.join(
        my_dir,
        '../data/v2.0/test_fails_on_invalid_external_ref/petstore.json')

    with open(petstore_path) as f:
        petstore_spec = json.load(f)

    petstore_url = 'file://{0}'.format(petstore_path)

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(petstore_spec, petstore_url)

    assert "`name` is missing" in str(excinfo.value)
