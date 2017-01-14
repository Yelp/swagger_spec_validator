# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import os

import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_json


def test_success():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_dir, '../data/v2.0/petstore.json')) as f:
        petstore_spec = json.load(f)
    validate_json(petstore_spec, 'swagger_spec_validator', 'schemas/v2.0/schema.json')


def test_failure():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_json({}, 'swagger_spec_validator', 'schemas/v2.0/schema.json')
    assert "'swagger' is a required property" in str(excinfo.value)
