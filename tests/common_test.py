import uuid
from unittest import mock

import importlib.resources

from swagger_spec_validator.common import read_file
from swagger_spec_validator.common import read_resource_file


def test_read_file():
    read_file("./tests/data/v2.0/petstore.json")


def test_read_resource_file(monkeypatch):
    resource_path = str(uuid.uuid4()) + ".json"

    with mock.patch("swagger_spec_validator.common.read_file") as m:
        read_resource_file(resource_path)
        read_resource_file(resource_path)

    m.assert_called_once_with(
        importlib.resources.files("swagger_spec_validator")
    )
