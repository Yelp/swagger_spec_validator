from jsonschema.validators import RefResolver
import pytest
from tests.validator20.conftest import get_spec_json_and_url
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


def test_success(petstore_dict):
    assert isinstance(validate_spec(petstore_dict), RefResolver)


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
    instagram_specs, _ = get_spec_json_and_url(
        '../data/v2.0/instagram.json'
    )
    validate_spec(instagram_specs)


def test_fails_on_invalid_external_ref_in_dict():
    # The external ref in petstore.json is valid.
    # The contents of the external ref (pet.json#/getall) is not - the 'name'
    # key in the parameter is missing.

    petstore_spec, petstore_url = get_spec_json_and_url(
        '../data/v2.0/test_fails_on_invalid_external_ref/petstore.json'
    )

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(petstore_spec, petstore_url)

    assert "is not valid under any of the given schemas" in str(excinfo.value)


def test_fails_on_invalid_external_ref_in_list():
    # The external ref in petstore.json is valid.
    # The contents of the external ref (pet.json#/get_all_parameters) is not
    # - the 'name' key in the parameter is missing.
    petstore_spec, petstore_url = get_spec_json_and_url(
        '../data/v2.0/test_fails_on_invalid_external_ref_in_list/petstore.json'
    )

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(petstore_spec, petstore_url)

    assert "is not valid under any of the given schemas" in str(excinfo.value)


@pytest.fixture
def node_spec():
    """Used in tests that have recursive $refs
    """
    return {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            },
            'child': {
                '$ref': '#/definitions/Node',
            },
        },
        'required': ['name']
    }


def test_recursive_ref(minimal_swagger_dict, node_spec):
    minimal_swagger_dict['definitions']['Node'] = node_spec
    validate_spec(minimal_swagger_dict)


def test_recursive_ref_failure(minimal_swagger_dict, node_spec):
    minimal_swagger_dict['definitions']['Node'] = node_spec
    # insert non-existent $ref
    node_spec['properties']['foo'] = {'$ref': '#/definitions/Foo'}
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(minimal_swagger_dict)
    assert 'Unresolvable JSON pointer' in str(excinfo.value)


def test_complicated_refs():
    # Split the swagger spec into a bunch of different json files and use
    # $refs all over to place to wire stuff together - see the test-data
    # files or this will make no sense whatsoever.
    file_path = '../../tests/data/v2.0/test_complicated_refs/swagger.json'
    swagger_dict, origin_url = get_spec_json_and_url(file_path)
    resolver = validate_spec(swagger_dict, spec_url=origin_url)

    # Hokey verification but better than nothing:
    #   If all the files with $refs were ingested and validated and an
    #   exception was not thrown, there should be 8 cached refs in the
    #   resolver's store:
    #
    #   6 json files from ../../tests/data/v2.0/tests_complicated_refs/*
    #   1 draft3 spec
    #   1 draft4 spec
    assert len(resolver.store) == 8


def test_specs_with_discriminator():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    validate_spec(swagger_dict)


def test_specs_with_discriminator_fail_because_not_required():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    swagger_dict['definitions']['GenericPet']['discriminator'] = 'name'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(swagger_dict)
    assert 'discriminator (name) must be defined a required property' in str(excinfo.value)


def test_specs_with_discriminator_fail_because_not_string():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    swagger_dict['definitions']['GenericPet']['discriminator'] = 'weight'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(swagger_dict)
    assert 'discriminator (weight) must be a string property' in str(excinfo.value)


def test_specs_with_discriminator_fail_because_not_in_properties():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    swagger_dict['definitions']['GenericPet']['discriminator'] = 'an_other_property'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(swagger_dict)
    assert 'discriminator (an_other_property) must be defined in properties' in str(excinfo.value)


def test_specs_with_discriminator_in_allOf():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    validate_spec(swagger_dict)


def test_specs_with_discriminator_in_allOf_fail_because_not_required():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    swagger_dict['definitions']['BaseObject']['discriminator'] = 'name'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(swagger_dict)
    assert 'discriminator (name) must be defined a required property' in str(excinfo.value)


def test_specs_with_discriminator_in_allOf_fail_because_not_string():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    swagger_dict['definitions']['BaseObject']['discriminator'] = 'weight'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(swagger_dict)
    assert 'discriminator (weight) must be a string property' in str(excinfo.value)


def test_specs_with_discriminator_in_allOf_fail_because_not_in_properties():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    swagger_dict['definitions']['BaseObject']['discriminator'] = 'an_other_property'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(swagger_dict)
    assert 'discriminator (an_other_property) must be defined in properties' in str(excinfo.value)
