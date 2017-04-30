# -*- coding: utf-8 -*-
from swagger_spec_validator.util import determine_swagger2dot0_object_type
from swagger_spec_validator.util import Swagger2dot0ObjectType


def test_determine_object_type_schema_succeed():
    assert determine_swagger2dot0_object_type(
        object_dict={'type': 'object'},
        possible_types=[Swagger2dot0ObjectType.SCHEMA],
    ) == {Swagger2dot0ObjectType.SCHEMA}


def test_determine_object_type_parameter_fail():
    assert determine_swagger2dot0_object_type(
        object_dict={'type': 'object'},
        possible_types=[Swagger2dot0ObjectType.PARAMETER],
    ) == set()


def test_determine_object_type_with_multiple_type_hints():
    assert determine_swagger2dot0_object_type(
        object_dict={
            'name': 'pung',
            'in': 'query',
            'description': 'true or false',
            'type': 'boolean',
        },
        possible_types=[Swagger2dot0ObjectType.PARAMETER, Swagger2dot0ObjectType.SCHEMA],
    ) == {Swagger2dot0ObjectType.PARAMETER}


def test_determine_object_type_with_no_type_hint():
    assert determine_swagger2dot0_object_type(
        object_dict={
            'get': {
                'responses': {
                    '200': {
                        'description': 'HTTP 200/OK',
                    }
                }
            }
        },
    ) == {Swagger2dot0ObjectType.PATH_ITEM}
