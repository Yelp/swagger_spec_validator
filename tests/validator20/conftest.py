import json
import os

import pytest

from swagger_spec_validator.common import get_uri_from_file_path
from tests import TESTS_BASE_PATH


@pytest.fixture(scope="session")
def petstore_contents():
    with open(TESTS_BASE_PATH + "/data/v2.0/petstore.json") as f:
        return f.read()


@pytest.fixture
def petstore_dict(petstore_contents):
    return json.loads(petstore_contents)


def get_spec_json_and_url(rel_path):
    abs_path = os.path.abspath(rel_path)
    with open(abs_path) as f:
        return json.loads(f.read()), get_uri_from_file_path(abs_path)
