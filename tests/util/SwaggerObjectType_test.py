# -*- coding: utf-8 -*-
import mock
from jsonschema import RefResolver, Draft4Validator

from swagger_spec_validator.common import read_file
from swagger_spec_validator.util import _initialize_Swagger2dot0ObjectType
from pkg_resources import resource_filename


def _reinitialize_Swagger2dot0ObjectType():
    # This is needed to re-initialize SwaggerObject with different files
    global Swagger2dot0ObjectType
    Swagger2dot0ObjectType = _initialize_Swagger2dot0ObjectType()


@mock.patch('swagger_spec_validator.util.read_file')
def test_SwaggerObjectType_with_no_mappings(mock_read_file):
    mock_read_file.return_value = {}
    _reinitialize_Swagger2dot0ObjectType()

    assert list(Swagger2dot0ObjectType) == []


def test_ensure_that_object_mappings_file_is_valid():
    _reinitialize_Swagger2dot0ObjectType()
    _object_mappings_path = resource_filename('swagger_spec_validator', 'schemas/v2.0/object_mappings.json')

    # Ensure that object_mappings file is valid
    Draft4Validator(schema={
        'additionalProperties': {
            'type': 'object',
            'required': [
                '$ref'
            ],
            'additionalProperties': False,
            'properties': {
                '$ref': {
                    'type': 'string',
                },
            },
        },
        'minProperties': 1,
    }).validate(read_file(_object_mappings_path))
    assert len(list(Swagger2dot0ObjectType)) >= 1


@mock.patch.object(RefResolver, 'resolve')
@mock.patch('swagger_spec_validator.util.read_file')
def test_SwaggerObjectType_mocked_mapping(mock_read_file, mock_resolve):
    reference_value = 'schema.json#/definitions/'
    dereferenced_schema = 'DEREFERENCED OBJECT'
    mock_read_file.return_value = {
        'KEY': {
            '$ref': reference_value,
        },
    }
    mock_resolve.return_value = 'URI', dereferenced_schema
    _reinitialize_Swagger2dot0ObjectType()

    assert Swagger2dot0ObjectType.KEY.name == 'KEY'
    assert Swagger2dot0ObjectType.KEY.value == dereferenced_schema

    mock_resolve.assert_called_once_with(reference_value)
