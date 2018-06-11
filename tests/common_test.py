# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from swagger_spec_validator.common import read_file


def test_read_file():
    read_file('./tests/data/v2.0/petstore.json')
