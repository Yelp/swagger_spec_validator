import json
import pytest

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


def test_empty_definitions_succes(minimal_swagger_dict):
    validate_spec(minimal_swagger_dict)
