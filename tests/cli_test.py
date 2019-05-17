# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from swagger_spec_validator.cli import main
from swagger_spec_validator.common import get_uri_from_file_path


def test_cli_main_goodfile():
    good_file = "./tests/data/v2.0/petstore.json"
    file_uri = get_uri_from_file_path(good_file)

    exit_code = main([file_uri])

    assert exit_code == 0


def test_cli_main_badfile():
    bad_file = "./tests/data/v2.0/test_fails_on_invalid_external_ref_in_list/petstore.json"
    file_uri = get_uri_from_file_path(bad_file)

    exit_code = main([file_uri])

    assert exit_code == 1


def test_cli_main_invalidfile():
    missing_file = "./tests/data/this-file-doesnt-exist.json"
    file_uri = get_uri_from_file_path(missing_file)

    exit_code = main([file_uri])

    assert exit_code == 1
