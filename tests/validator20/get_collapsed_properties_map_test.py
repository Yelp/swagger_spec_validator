# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools

from swagger_spec_validator.validator20 import deref
from swagger_spec_validator.validator20 import get_collapsed_properties_type_mappings
from swagger_spec_validator.validator20 import validate_json


def get_deref(spec_dict):
    swagger_resolver = validate_json(
        spec_dict,
        'schemas/v2.0/schema.json',
    )
    return functools.partial(deref, resolver=swagger_resolver)


def test_get_collapsed_properties_type_mapping_simple_case(polymorphic_swagger2dot0_specs_dict):
    required_parameters, not_required_parameters = get_collapsed_properties_type_mappings(
        definition=polymorphic_swagger2dot0_specs_dict['definitions']['GenericPet'],
        deref=get_deref(polymorphic_swagger2dot0_specs_dict),
    )
    assert required_parameters == {'type': 'string', 'weight': 'integer'}
    assert not_required_parameters == {'name': 'string'}


def test_get_collapsed_properties_type_mapping_allOf_add_required_property(polymorphic_swagger2dot0_specs_dict):
    required_parameters, not_required_parameters = get_collapsed_properties_type_mappings(
        definition=polymorphic_swagger2dot0_specs_dict['definitions']['Dog'],
        deref=get_deref(polymorphic_swagger2dot0_specs_dict),
    )
    assert required_parameters == {'type': 'string', 'weight': 'integer', 'birth_date': 'string'}
    assert not_required_parameters == {'name': 'string'}


def test_get_collapsed_properties_type_mapping_allOf_add_not_required_property(polymorphic_swagger2dot0_specs_dict):
    required_parameters, not_required_parameters = get_collapsed_properties_type_mappings(
        definition=polymorphic_swagger2dot0_specs_dict['definitions']['Cat'],
        deref=get_deref(polymorphic_swagger2dot0_specs_dict),
    )
    assert required_parameters == {'type': 'string', 'weight': 'integer'}
    assert not_required_parameters == {'name': 'string', 'color': 'string'}
