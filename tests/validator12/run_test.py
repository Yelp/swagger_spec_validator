from __future__ import print_function
import glob
import json
import os
import os.path

import jsonschema.exceptions

from swagger_spec_validator.validator12 import validate_api_declaration
from swagger_spec_validator.validator12 import validate_resource_listing
from swagger_spec_validator import SwaggerValidationError


def run_json_tests_with_func(json_test_paths, func):
    """Run the specified test function over a list of JSON test files."""

    for json_test_path in sorted(json_test_paths):
        with open(json_test_path) as fd:
            test_data = json.load(fd)

        # Grab last two components from test_path
        # e.g. "api_declarations/array_nested_fail.json"
        test_name = os.sep.join(json_test_path.split(os.sep)[-2:])

        print('Testing %s...' % test_name)

        if test_name.endswith('_pass.json'):
            func(test_data)
        elif test_name.endswith('_fail.json'):
            try:
                func(test_data)
            except (SwaggerValidationError, jsonschema.exceptions.ValidationError):
                pass
            else:
                raise ValueError('Validation error did not occur')
        else:
            raise ValueError('Invalid test name')


def test_main():
    my_dir = os.path.abspath(os.path.dirname(__file__))

    run_json_tests_with_func(
        glob.glob(os.path.join(my_dir, '../data/v1.2/api_declarations/*.json')),
        validate_api_declaration)

    run_json_tests_with_func(
        glob.glob(os.path.join(my_dir, '../data/v1.2/resource_listings/*.json')),
        validate_resource_listing)
