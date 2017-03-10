import json
import os

from jsonschema.validators import RefResolver
import pytest
from six.moves.urllib import parse as urlparse

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
    assert isinstance(validate_spec(json.loads(petstore_contents)),
                      RefResolver)


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


def test_fails_on_invalid_external_ref_in_dict():
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

    assert "is not valid under any of the given schemas" in str(excinfo.value)


def test_fails_on_invalid_external_ref_in_list():
    # The external ref in petstore.json is valid.
    # The contents of the external ref (pet.json#/get_all_parameters) is not
    # - the 'name' key in the parameter is missing.
    my_dir = os.path.abspath(os.path.dirname(__file__))

    petstore_path = os.path.join(
        my_dir,
        '../data/v2.0/test_fails_on_invalid_external_ref_in_list/petstore.json')

    with open(petstore_path) as f:
        petstore_spec = json.load(f)

    petstore_url = 'file://{0}'.format(petstore_path)

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

    def get_spec_json_and_url(rel_url):
        my_dir = os.path.abspath(os.path.dirname(__file__))
        abs_path = os.path.join(my_dir, rel_url)
        with open(abs_path) as f:
            return json.loads(f.read()), urlparse.urljoin('file:', abs_path)

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
    #   7 json files from ../../tests/data/v2.0/tests_complicated_refs/*
    #   1 draft3 spec
    #   1 draft4 spec
    assert len(resolver.store) == 9
