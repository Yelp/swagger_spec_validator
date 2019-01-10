# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_validator.common import SwaggerValidationWarning
from swagger_spec_validator.validator20 import validate_references


# @pytest.mark.parametrize(
#     'raw_spec',
#     [
#         {'$ref': '#/'},
#         {'description': 'Description sibling is acceptable', '$ref': '#/'},
#         [{'$ref': '#/'}],
#     ],
# )
# def test_validate_valid_references(recwarn, raw_spec):
#     validate_references(raw_spec=raw_spec, deref=lambda x: x)
#     assert len(recwarn) == 0


@pytest.mark.parametrize(
    'raw_spec, expected_warning_messages',
    [
        (
            {'sibling-attribute': '', '$ref': '#/'},
            (
                'Found "$ref: #/" with siblings that will be overwritten. '
                'See https://stackoverflow.com/a/48114924 for more information. (path #)',
            ),
        ),
        (
            [{'sibling-attribute': '', '$ref': '#/'}],
            (
                'Found "$ref: #/" with siblings that will be overwritten. '
                'See https://stackoverflow.com/a/48114924 for more information. (path #/0)',
            ),
        ),
        (
            {'$ref': None},
            (
                'Identified $ref with None value. This usually represent an error on the specs even '
                'if this does not make them invalid as the location of the reference could tolerate '
                'a None value. (path #)',
            ),
        ),
        (
            {'key': {'$ref': None}},
            (
                'Identified $ref with None value. This usually represent an error on the specs even '
                'if this does not make them invalid as the location of the reference could tolerate '
                'a None value. (path #/key)',
            ),
        ),
        (
            {'key': [{'sibling-attribute': 1, '$ref': None}]},
            (
                'Found "$ref: None" with siblings that will be overwritten. '
                'See https://stackoverflow.com/a/48114924 for more information. (path #/key/0)',
                'Identified $ref with None value. This usually represent an error on the specs even '
                'if this does not make them invalid as the location of the reference could tolerate '
                'a None value. (path #/key/0)',
            ),
        ),
    ],
)
def test_validate_references_to_warn(raw_spec, expected_warning_messages):
    with pytest.warns(SwaggerValidationWarning) as warninfo:
        validate_references(raw_spec=raw_spec, deref=lambda x: x)

    assert sorted(expected_warning_messages) == sorted(str(warning.message) for warning in warninfo.list)
