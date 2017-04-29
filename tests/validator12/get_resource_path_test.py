# -*- coding: utf-8 -*-
import pytest

from swagger_spec_validator.validator12 import get_resource_path


def test_fetch_from_file_uri_success():
    url, resource = "file://bla/bar", "/foo"
    assert "file://bla/foo.json", get_resource_path(url, resource)


def test_fetch_from_http_uri_success():
    url, resource = "http://bla/bar", "/foo"
    assert "http://bla/bar/foo", get_resource_path(url, resource)


def test_fetch_from_bad_file_uri_fail():
    with pytest.raises(AssertionError):
        url, resource = "file://bla/bar", "no_slash"
        get_resource_path(url, resource)
