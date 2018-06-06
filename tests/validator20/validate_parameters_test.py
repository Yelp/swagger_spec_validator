# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_parameters


@pytest.mark.parametrize(
    'top_level_parameters',
    [
        {},
        {
            'Offset': {
                'in': 'query',
                'name': 'offset',
                'type': 'integer',
            },
        },
        {
            'AcceptedLanguage': {
                'in': 'header',
                'name': 'Accepted-Language',
                'type': 'string',
            },
        },
    ]
)
def test_valid_top_level_parameters(top_level_parameters):
    validate_parameters(top_level_parameters, deref=lambda x: x)


@pytest.mark.parametrize(
    'top_level_parameters, expected_exception_string',
    [
        [
            {
                'Offset': {
                    'in': 'body',
                    'name': 'body',
                },
            },
            'Body parameter in `#/parameters/Offset` does not specify `schema`.',
        ],
        [
            {
                'ParameterWithoutType': {
                    'in': 'header',
                    'name': 'a-random-parameter',
                },
            },
            'Non-Body parameter in `#/parameters/ParameterWithoutType` does not specify `type`.',
        ],
        [
            {
                'ListOfIntegers': {
                    'in': 'header',
                    'name': 'Accepted-Language',
                    'type': 'array',
                },
            },
            'Non-Body array parameter in `#/parameters/ListOfIntegers` does not specify `items`.',
        ],
    ]
)
def test_invalid_top_level_parameters(top_level_parameters, expected_exception_string):
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_parameters(top_level_parameters, deref=lambda x: x)

    assert str(excinfo.value) == expected_exception_string
