from unittest.mock import Mock

import pytest
from jsonschema.exceptions import RefResolutionError
from jsonschema.validators import RefResolver

from swagger_spec_validator.validator20 import deref


def test_none():
    assert deref(None, Mock(spec=RefResolver)) is None


def test_not_dict():
    assert deref(1, Mock(spec=RefResolver)) == 1


def test_not_ref():
    input = {"type": "object"}
    assert deref(input, Mock(spec=RefResolver)) == input


def test_ref():
    ref_dict = {"$ref": "#/definitions/Foo"}
    definitions = {"definitions": {"Foo": "bar"}}
    assert deref(ref_dict, RefResolver("", definitions)) == "bar"


def test_ref_not_found():
    ref_dict = {"$ref": "#/definitions/Foo"}
    definitions = {}
    with pytest.raises(RefResolutionError) as excinfo:
        deref(ref_dict, RefResolver("", definitions))
    assert "Unresolvable JSON pointer" in str(excinfo.value)
