# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from swagger_spec_validator.common import read_file


def test_read_file():
    read_file(os.path.join(os.path.dirname(__file__), 'data/v2.0/petstore.json'))
