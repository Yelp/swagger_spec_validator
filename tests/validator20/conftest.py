import os

import pytest


@pytest.fixture(scope='session')
def petstore_contents():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_dir, '../data/v2.0/petstore.json')) as f:
        return f.read()
