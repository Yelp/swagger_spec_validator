import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_definitions


@pytest.mark.parametrize(
    "property_spec",
    [
        {"type": "integer", "default": 1},
        {"type": "boolean", "default": True},
        {"type": "null", "default": None},
        {"type": "number", "default": 2},
        {"type": "number", "default": 3.4},
        {"type": "object", "default": {"a_random_property": "valid"}},
        {"type": "array", "items": {"type": "integer"}, "default": [5, 6, 7]},
        {"default": -1},  # if type is not defined any value is a valid value
        {"type": "string", "default": ""},
    ],
)
def test_api_check_default_succeed(property_spec):
    definitions = {
        "injected_definition": {
            "properties": {
                "property": property_spec,
            },
        },
    }

    # Success if no exception are raised
    validate_definitions(definitions, lambda x: x)


@pytest.mark.parametrize(
    "property_spec, validator, instance",
    [
        [
            {"type": "integer", "default": "wrong_type"},
            "type",
            "wrong_type",
        ],
        [
            {"type": "boolean", "default": "wrong_type"},
            "type",
            "wrong_type",
        ],
        [
            {"type": "null", "default": "wrong_type"},
            "type",
            "wrong_type",
        ],
        [
            {"type": "number", "default": "wrong_type"},
            "type",
            "wrong_type",
        ],
        [
            {"type": "object", "default": "wrong_type"},
            "type",
            "wrong_type",
        ],
        [
            {"type": "array", "default": "wrong_type"},
            "type",
            "wrong_type",
        ],
        [
            {"type": "string", "default": -1},
            "type",
            -1,
        ],
        [
            {"type": "string", "minLength": 100, "default": "short_string"},
            "minLength",
            "short_string",
        ],
    ],
)
def test_api_check_default_fails(property_spec, validator, instance):
    definitions = {
        "injected_definition": {
            "properties": {
                "property": property_spec,
            },
        },
    }

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_definitions(definitions, lambda x: x)

    validation_error = excinfo.value.args[1]
    assert validation_error.instance == instance
    assert validation_error.validator == validator


def test_multiple_types_fail():
    definitions = {
        "definition_1": {
            "type": ["number", "boolean"],
        },
    }

    with pytest.raises(
        SwaggerValidationError,
        match=r"In definition of .*, type must be a string; lists are not allowed \(.*\)",
    ) as excinfo:
        validate_definitions(definitions, lambda x: x)

    assert str(definitions["definition_1"]["type"]) in str(excinfo.value)


def test_type_array_with_items_succeed_validation():
    definitions = {
        "definition_1": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    }

    # Success if no exception are raised
    validate_definitions(definitions, lambda x: x)


def test_type_array_without_items_succeed_fails():
    definitions = {
        "definition_1": {
            "type": "array",
        },
    }

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_definitions(definitions, lambda x: x)

    assert (
        str(excinfo.value)
        == "Definition of type array must define `items` property (definition #/definitions/definition_1)."
    )


def test_inline_model_is_not_valid_validation_fails():
    definitions = {
        "definition_1": {
            "properties": {
                "property": {
                    "type": "array",
                },
            },
        },
    }

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_definitions(definitions, lambda x: x)

    assert (
        str(excinfo.value) == "Definition of type array must define `items` property "
        "(definition #/definitions/definition_1/properties/property)."
    )
