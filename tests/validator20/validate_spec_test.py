# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest
from jsonschema.validators import RefResolver

from swagger_spec_validator.common import read_file
from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec
from tests.conftest import get_url


@pytest.fixture
def minimal_swagger2dot0_specs_dict(test_dir):
    return read_file(get_url(os.path.join(test_dir, 'data/v2.0/minimal.yaml')))


@pytest.fixture
def minimal_swagger_dict():
    """Return minimal dict that represents a swagger spec - useful as a base template."""
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


def test_success(petstore_swagger2dot0_specs_dict):
    assert isinstance(validate_spec(petstore_swagger2dot0_specs_dict), RefResolver)


def test_definitons_not_present_success(minimal_swagger2dot0_specs_dict):
    del minimal_swagger2dot0_specs_dict['definitions']
    validate_spec(minimal_swagger2dot0_specs_dict)


def test_empty_definitions_success(minimal_swagger2dot0_specs_dict):
    validate_spec(minimal_swagger2dot0_specs_dict)


def test_api_parameters_as_refs(test_dir):
    # Verify issue #29 - instragram.json comes from:
    #
    # http://editor.swagger.io/#/
    #    -> File
    #       -> Open Example...
    #          -> instagram.yaml
    #
    # and then export it to a json file.
    validate_spec(read_file(get_url(os.path.join(test_dir, 'data/v2.0/instagram.json'))))


def test_fails_on_invalid_external_ref_in_dict(test_dir):
    # The external ref in petstore.json is valid.
    # The contents of the external ref (pet.json#/getall) is not - the 'name'
    # key in the parameter is missing.

    invalid_refs_petstore_url = get_url(os.path.join(test_dir, 'data/v2.0/test_fails_on_invalid_external_ref/petstore.json'))
    invalid_refs_petstore_dict = read_file(invalid_refs_petstore_url)
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(
            spec_dict=invalid_refs_petstore_dict,
            spec_url=invalid_refs_petstore_url,
        )

    assert "is not valid under any of the given schemas" in str(excinfo.value)


def test_fails_on_invalid_external_ref_in_list(test_dir):
    # The external ref in petstore.json is valid.
    # The contents of the external ref (pet.json#/get_all_parameters) is not
    # - the 'name' key in the parameter is missing.

    invalid_refs_petstore_url = get_url(os.path.join(test_dir, 'data/v2.0/test_fails_on_invalid_external_ref_in_list/petstore.json'))
    invalid_refs_petstore_dict = read_file(invalid_refs_petstore_url)

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(
            spec_dict=invalid_refs_petstore_dict,
            spec_url=invalid_refs_petstore_url,
        )

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


def test_recursive_ref(minimal_swagger2dot0_specs_dict, node_spec):
    minimal_swagger2dot0_specs_dict['definitions']['Node'] = node_spec
    validate_spec(minimal_swagger2dot0_specs_dict)


def test_recursive_ref_failure(minimal_swagger2dot0_specs_dict, node_spec):
    minimal_swagger2dot0_specs_dict['definitions']['Node'] = node_spec
    # insert non-existent $ref
    node_spec['properties']['foo'] = {'$ref': '#/definitions/Foo'}
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(minimal_swagger2dot0_specs_dict)
    assert 'Unresolvable JSON pointer' in str(excinfo.value)


def test_complicated_refs(test_dir):
    # Split the swagger spec into a bunch of different json files and use
    # $refs all over to place to wire stuff together - see the test-data
    # files or this will make no sense whatsoever.
    complicated_specs_url = get_url(os.path.join(test_dir, 'data/v2.0/test_complicated_refs/swagger.json'))
    complicated_specs_dict = read_file(complicated_specs_url)

    resolver = validate_spec(spec_dict=complicated_specs_dict, spec_url=complicated_specs_url)

    # Hokey verification but better than nothing:
    #   If all the files with $refs were ingested and validated and an
    #   exception was not thrown, there should be 8 cached refs in the
    #   resolver's store:
    #
    #   6 json files from ../../tests/data/v2.0/tests_complicated_refs/*
    #   1 yaml files from ../../tests/data/v2.0/tests_complicated_refs/*
    #   1 draft3 spec
    #   1 draft4 spec
    assert len(resolver.store) == 9


def test_specs_with_discriminator(polymorphic_swagger2dot0_specs_dict):
    validate_spec(polymorphic_swagger2dot0_specs_dict)


def test_specs_with_discriminator_fail_because_not_required(polymorphic_swagger2dot0_specs_dict):
    polymorphic_swagger2dot0_specs_dict['definitions']['GenericPet']['discriminator'] = 'name'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(polymorphic_swagger2dot0_specs_dict)
    assert 'discriminator (name) must be defined a required property' in str(excinfo.value)


def test_specs_with_discriminator_fail_because_not_string(polymorphic_swagger2dot0_specs_dict):
    polymorphic_swagger2dot0_specs_dict['definitions']['GenericPet']['discriminator'] = 'weight'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(polymorphic_swagger2dot0_specs_dict)
    assert 'discriminator (weight) must be a string property' in str(excinfo.value)


def test_specs_with_discriminator_fail_because_not_in_properties(polymorphic_swagger2dot0_specs_dict):
    polymorphic_swagger2dot0_specs_dict['definitions']['GenericPet']['discriminator'] = 'an_other_property'

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(polymorphic_swagger2dot0_specs_dict)
    assert 'discriminator (an_other_property) must be defined in properties' in str(excinfo.value)


@pytest.fixture
def default_checks_spec_dict(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['bool_string'] = {
        'properties': {
            'value': {
                'type': 'string', 'enum': ['True', 'False'],
            },
        },
    }
    return minimal_swagger_dict


@pytest.mark.parametrize(
    'property_spec',
    [
        {'type': 'integer', 'default': 1},
        {'type': 'boolean', 'default': True},
        {'type': 'null', 'default': None},
        {'type': 'number', 'default': 2},
        {'type': 'number', 'default': 3.4},
        {'type': 'object', 'default': {'a_random_property': 'valid'}},
        {'type': 'array', 'default': [5, 6, 7]},
        {'type': 'string', 'default': ''},
        {'default': -1},  # if type is not defined any value is a valid value
        {'type': ['number', 'boolean'], 'default': 8},
        {'type': ['number', 'boolean'], 'default': False},
        {'type': 'array', 'items': {'$ref': '#/definitions/bool_string'}, 'default': [{'value': 'False'}]},
    ],
)
def test_valid_specs_with_check_of_default_types(default_checks_spec_dict, property_spec):
    default_checks_spec_dict['definitions']['injected_definition'] = {
        'properties': {'property': property_spec},
    }
    # Success if no exception are raised
    validate_spec(default_checks_spec_dict)


@pytest.mark.parametrize(
    'property_spec, validator, instance',
    [
        [
            {'type': 'integer', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'boolean', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'null', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'number', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'object', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'array', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'string', 'default': -1},
            'type', -1,
        ],
        [
            {'type': 'string', 'minLength': 100, 'default': 'short_string'},
            'minLength', 'short_string',
        ],
        [
            {'type': ['number', 'boolean'], 'default': 'not_a_number_or_boolean'},
            'type', 'not_a_number_or_boolean',
        ],
        [
            {'type': 'array', 'items': {'$ref': '#/definitions/bool_string'}, 'default': [{'value': 'not_valid'}]},
            'enum', 'not_valid',
        ],
    ],
)
def test_failure_due_to_wrong_default_type(default_checks_spec_dict, property_spec, validator, instance):
    default_checks_spec_dict['definitions']['injected_definition'] = {
        'properties': {'property': property_spec},
    }
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec(default_checks_spec_dict)

    validation_error = excinfo.value.args[1]
    assert validation_error.instance == instance
    assert validation_error.validator == validator
