# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_json


def test_success(petstore_swagger2dot0_specs_dict):
    validate_json(petstore_swagger2dot0_specs_dict, 'schemas/v2.0/schema.json')


def test_failure():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_json({}, 'schemas/v2.0/schema.json')
    assert "'swagger' is a required property" in str(excinfo.value)
