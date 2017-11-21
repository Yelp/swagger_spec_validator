# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec


def test_failure_on_duplicate_api_parameters(petstore_swagger2dot0_specs_dict):
    param1 = {"name": "foo", "in": "query", "type": "string"}
    param2 = {"name": "foo", "in": "query", "type": "integer"}
    petstore_swagger2dot0_specs_dict['paths']['/pet']['parameters'] = [param1, param2]
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(petstore_swagger2dot0_specs_dict)
    assert ("Duplicate param found with (name, in): {}".format(("foo", "query")) in str(exc_info.value))


def test_failure_on_duplicate_operation_parameters(petstore_swagger2dot0_specs_dict):
    param1 = {"name": "foo", "in": "query", "type": "string"}
    param2 = {"name": "foo", "in": "query", "type": "integer"}
    petstore_swagger2dot0_specs_dict['paths']['/pet']['post']['parameters'].extend([param1, param2])
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(petstore_swagger2dot0_specs_dict)
    assert ("Duplicate param found with (name, in): {}".format(("foo", "query")) in str(exc_info.value))


def test_failure_on_unresolvable_path_parameter(petstore_swagger2dot0_specs_dict):
    petstore_swagger2dot0_specs_dict['paths']['/pet/{foo}'] = petstore_swagger2dot0_specs_dict['paths']['/pet']
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(petstore_swagger2dot0_specs_dict)
    assert "Path parameter 'foo' used is not documented on '/pet/{foo}'" in str(exc_info.value)


def test_failure_on_path_parameter_used_but_not_defined(petstore_swagger2dot0_specs_dict):
    petstore_swagger2dot0_specs_dict['paths']['/user/{username}']['get']['parameters'][0]['name'] = '_'
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(petstore_swagger2dot0_specs_dict)
    assert "Path parameter 'username' used is not documented on '/user/{username}'" in str(exc_info.value)


def test_failure_on_unresolvable_ref_of_props_required_list(petstore_swagger2dot0_specs_dict):
    petstore_swagger2dot0_specs_dict['definitions']['Pet']['required'].append('bla')
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(petstore_swagger2dot0_specs_dict)
    assert ("Required list has properties not defined: {}".format(['bla']) in str(exc_info.value))


def test_failure_on_unresolvable_model_reference_from_model(petstore_swagger2dot0_specs_dict):
    petstore_swagger2dot0_specs_dict['definitions']['Pet']['properties']['category']['$ref'] = '_'
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(petstore_swagger2dot0_specs_dict)
    assert 'unknown url type:' in str(exc_info.value)


def test_failure_on_unresolvable_model_reference_from_param(petstore_swagger2dot0_specs_dict):
    param = petstore_swagger2dot0_specs_dict['paths']['/pet']['post']['parameters'][0]
    param['schema']['$ref'] = '#/definitions/bla'
    with pytest.raises(SwaggerValidationError):
        validate_spec(petstore_swagger2dot0_specs_dict)


def test_failure_on_unresolvable_model_reference_from_resp(petstore_swagger2dot0_specs_dict):
    resp = petstore_swagger2dot0_specs_dict['paths']['/pet/findByStatus']['get']['responses']
    resp['200']['schema']['items']['$ref'] = '#/definitions/bla'
    with pytest.raises(SwaggerValidationError):
        validate_spec(petstore_swagger2dot0_specs_dict)

# TODO: Add warning validations for unused models, path parameter & responses
# TODO: Add validations for cyclic model definitions
