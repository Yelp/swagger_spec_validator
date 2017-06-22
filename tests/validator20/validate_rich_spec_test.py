# -*- coding: utf-8 -*-
import json
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec


@pytest.fixture
def swagger_spec(petstore_contents):
    return json.loads(petstore_contents)


def test_failure_on_duplicate_api_parameters(swagger_spec):
    param1 = {"name": "foo", "in": "query", "type": "string"}
    param2 = {"name": "foo", "in": "query", "type": "integer"}
    swagger_spec['paths']['/pet']['parameters'] = [param1, param2]
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(swagger_spec)
    assert ("Duplicate param found with (name, in): {}".format(("foo", "query")) in str(exc_info.value))


def test_failure_on_duplicate_operation_parameters(swagger_spec):
    param1 = {"name": "foo", "in": "query", "type": "string"}
    param2 = {"name": "foo", "in": "query", "type": "integer"}
    swagger_spec['paths']['/pet']['post']['parameters'].extend([param1, param2])
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(swagger_spec)
    assert ("Duplicate param found with (name, in): {}".format(("foo", "query")) in str(exc_info.value))


def test_failure_on_unresolvable_path_parameter(swagger_spec):
    swagger_spec['paths']['/pet/{foo}'] = swagger_spec['paths']['/pet']
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(swagger_spec)
    assert "Path parameter 'foo' used is not documented on '/pet/{foo}'" in str(exc_info.value)


def test_failure_on_path_parameter_used_but_not_defined(swagger_spec):
    swagger_spec['paths']['/user/{username}']['get']['parameters'][0]['name'] = '_'
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(swagger_spec)
    assert "Path parameter 'username' used is not documented on '/user/{username}'" in str(exc_info.value)


def test_failure_on_unresolvable_ref_of_props_required_list(swagger_spec):
    swagger_spec['definitions']['Pet']['required'].append('bla')
    with pytest.raises(SwaggerValidationError) as exc_info:
        validate_spec(swagger_spec)
    assert ("Required list has properties not defined: {}".format(['bla']) in str(exc_info.value))


def test_failure_on_unresolvable_model_reference_from_model(swagger_spec):
    swagger_spec['definitions']['Pet']['properties']['category']['$ref'] = '_'
    with pytest.raises(SwaggerValidationError):
        validate_spec(swagger_spec)


def test_failure_on_unresolvable_model_reference_from_param(swagger_spec):
    param = swagger_spec['paths']['/pet']['post']['parameters'][0]
    param['schema']['$ref'] = '#/definitions/bla'
    with pytest.raises(SwaggerValidationError):
        validate_spec(swagger_spec)


def test_failure_on_unresolvable_model_reference_from_resp(swagger_spec):
    resp = swagger_spec['paths']['/pet/findByStatus']['get']['responses']
    resp['200']['schema']['items']['$ref'] = '#/definitions/bla'
    with pytest.raises(SwaggerValidationError):
        validate_spec(swagger_spec)

# TODO: Add warning validations for unused models, path parameter & responses
# TODO: Add validations for cyclic model definitions
