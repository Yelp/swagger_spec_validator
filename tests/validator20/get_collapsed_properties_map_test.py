# -*- coding: utf-8 -*-
import functools
from tests.validator20.conftest import get_spec_json_and_url
from swagger_spec_validator.validator20 import validate_json, deref
from swagger_spec_validator.validator20 import get_collapsed_properties_type_mappings


def get_deref(spec_dict):
    swagger_resolver = validate_json(
        spec_dict,
        'schemas/v2.0/schema.json',
    )
    return functools.partial(deref, resolver=swagger_resolver)


def test_get_collapsed_properties_type_mapping_simple_case():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    required_parameters, not_required_parameters = get_collapsed_properties_type_mappings(
        definition=swagger_dict['definitions']['GenericPet'],
        deref=get_deref(swagger_dict),
    )
    assert required_parameters == {'type': 'string', 'weight': 'integer'}
    assert not_required_parameters == {'name': 'string'}


def test_get_collapsed_properties_type_mapping_allOf_add_required_property():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    required_parameters, not_required_parameters = get_collapsed_properties_type_mappings(
        definition=swagger_dict['definitions']['Dog'],
        deref=get_deref(swagger_dict),
    )
    assert required_parameters == {'type': 'string', 'weight': 'integer', 'birth_date': 'string'}
    assert not_required_parameters == {'name': 'string'}


def test_get_collapsed_properties_type_mapping_allOf_add_not_required_property():
    file_path = '../../tests/data/v2.0/test_polymorphic_specs/swagger.json'
    swagger_dict, _ = get_spec_json_and_url(file_path)

    required_parameters, not_required_parameters = get_collapsed_properties_type_mappings(
        definition=swagger_dict['definitions']['Cat'],
        deref=get_deref(swagger_dict),
    )
    assert required_parameters == {'type': 'string', 'weight': 'integer'}
    assert not_required_parameters == {'name': 'string', 'color': 'string'}
