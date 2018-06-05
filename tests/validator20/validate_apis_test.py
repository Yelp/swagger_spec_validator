# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_apis


RESPONSES = {
    'default': {
        'description': 'random description',
    },
}


def test_api_level_params_ok():
    # Parameters defined at the API level apply to all operations within that
    # API. Make sure we don't treat the API level parameters as an operation
    # since they are peers.
    apis = {
        '/tags/{tag-name}': {
            'parameters': [
                {
                    'name': 'tag-name',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                },
            ],
            'get': {
                'responses': RESPONSES,
            },
        },
    }
    # Success == no exception thrown
    validate_apis(apis, lambda x: x)


def test_api_level_x_hyphen_ok():
    # Elements starting with "x-" should be ignored
    apis = {
        '/tags/{tag-name}': {
            'x-ignore-me': 'DO NOT LOOK AT ME!',
            'get': {
                'parameters': [
                    {
                        'name': 'tag-name',
                        'in': 'path',
                        'type': 'string',
                    }
                ],
                'responses': RESPONSES,
            }
        }
    }
    # Success == no exception thrown
    validate_apis(apis, lambda x: x)


@pytest.mark.parametrize(
    'partial_parameter_spec',
    [
        {'type': 'integer', 'default': 1},
        {'type': 'boolean', 'default': True},
        {'type': 'null', 'default': None},
        {'type': 'number', 'default': 2},
        {'type': 'number', 'default': 3.4},
        {'type': 'object', 'default': {'a_random_property': 'valid'}},
        {'type': 'array', 'items': {'type': 'integer'}, 'default': [5, 6, 7]},
        {'type': 'string', 'default': ''},
        {'type': ['number', 'boolean'], 'default': 8},
        {'type': ['number', 'boolean'], 'default': False},
    ],
)
def test_api_check_default_succeed(partial_parameter_spec):
    apis = {
        '/api': {
            'get': {
                'parameters': [
                    dict({'name': 'param', 'in': 'query'}, **partial_parameter_spec),
                ],
                'responses': RESPONSES,
            },
        },
    }

    # Success if no exception are raised
    validate_apis(apis, lambda x: x)


@pytest.mark.parametrize(
    'partial_parameter_spec, validator, instance',
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
    ],
)
def test_api_check_default_fails(partial_parameter_spec, validator, instance):
    apis = {
        '/api': {
            'get': {
                'parameters': [
                    dict({'name': 'param', 'in': 'query'}, **partial_parameter_spec),
                ],
                'responses': RESPONSES,
            },
        },
    }

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_apis(apis, lambda x: x)

    validation_error = excinfo.value.args[1]
    assert validation_error.instance == instance
    assert validation_error.validator == validator


@pytest.mark.parametrize(
    'apis',
    [
        {
            '/api': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'responses': {},
                },
                'post': {
                    'operationId': 'duplicateOperationId',
                    'responses': {},
                },
            },
        },
        {
            '/api1': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'responses': {},
                },
            },
            '/api2': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'responses': {},
                },
            },
        },
        {
            '/api1': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'tags': ['tag1', 'tag2'],
                    'responses': {},
                },
            },
            '/api2': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'tags': ['tag1'],
                    'responses': {},
                },
            },
        },
    ]
)
def test_duplicate_operationIds_fails(apis):
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_apis(apis, lambda x: x)

    swagger_validation_error = excinfo.value
    error_message = swagger_validation_error.args[0]

    assert error_message == "Duplicate operationId: duplicateOperationId"


@pytest.mark.parametrize(
    'apis',
    [
        {
            '/api1': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'tags': ['tag1'],
                    'responses': {},
                },
            },
            '/api2': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'tags': ['tag2'],
                    'responses': {},
                },
            },
            '/api3': {
                'get': {
                    'operationId': 'duplicateOperationId',
                    'responses': {},
                },
            },
        },
    ]
)
def test_duplicate_operationIds_succeeds_if_tags_differ(apis):
    validate_apis(apis, lambda x: x)
