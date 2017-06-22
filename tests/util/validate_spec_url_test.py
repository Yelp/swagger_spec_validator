# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import validate_spec_url


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert '<urlopen error [Errno -2] Name or service not known>' in str(excinfo.value) or \
           '<urlopen error [Errno 8] nodename nor servname provided, or not known' in str(excinfo.value)


@mock.patch('swagger_spec_validator.util.read_url')
@mock.patch('swagger_spec_validator.util.get_validator')
def test_validate_spec_url_success(mock_get_validator, mock_read_url):
    spec_url = mock.Mock()
    validate_spec_url(spec_url)
    mock_read_url.assert_called_once_with(spec_url)
    mock_get_validator.assert_called_once_with(mock_read_url.return_value, spec_url)
