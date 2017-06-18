# -*- coding: utf-8 -*-
import os
import yaml

import mock
import pytest
import httpretty

from swagger_spec_validator.common import read_file
from swagger_spec_validator.common import read_url
from tests.conftest import get_url


@pytest.mark.parametrize(
    'file_path',
    [
        'data/v2.0/petstore.json',
        'data/v2.0/minimal.yaml',
    ]
)
@mock.patch('swagger_spec_validator.common.safe_load')
def test_read_file_valid(mock_safe_load, test_dir, file_path):
    abs_file_path = os.path.join(test_dir, file_path)
    f = read_file(abs_file_path)

    assert mock_safe_load.called
    assert f == mock_safe_load.return_value


def test_read_file_invalid(test_dir):
    abs_file_path = os.path.join(test_dir, 'data/invalid_json_invalid_yaml')

    with pytest.raises(yaml.parser.ParserError):
        read_file(abs_file_path)


@pytest.mark.parametrize(
    'file_path',
    [
        'data/v2.0/petstore.json',
        'data/v2.0/minimal.yaml',
    ]
)
@mock.patch('swagger_spec_validator.common.safe_load')
def test_read_url_reads_local_file(mock_safe_load, test_dir, file_path):
    abs_file_path = os.path.join(test_dir, file_path)
    url = get_url(abs_file_path)
    f = read_url(url)

    assert mock_safe_load.called
    assert f == mock_safe_load.return_value


@httpretty.activate
@pytest.mark.parametrize(
    'url, file_path',
    [
        ('http://service.my/swagger.json', 'data/v2.0/petstore.json'),
        ('http://service.my/swagger.yaml', 'data/v2.0/minimal.yaml'),
        ('http://service.my/swagger.txt', 'data/v2.0/petstore.json'),
    ]
)
@mock.patch('swagger_spec_validator.common.safe_load')
def test_read_url_reads_remote(mock_safe_load, test_dir, url, file_path):
    abs_file_path = os.path.join(test_dir, file_path)
    with open(abs_file_path) as fp:
        file_content = fp.read()

    content_type_mapping = {
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.yaml': 'application/yaml',
    }

    httpretty.register_uri(
        httpretty.GET, url,
        body=file_content,
        content_type=content_type_mapping[os.path.splitext(file_path)[1]],
    )

    f = read_url(url)

    assert mock_safe_load.called
    assert f == mock_safe_load.return_value
