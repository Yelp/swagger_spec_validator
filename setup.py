from __future__ import absolute_import, division, print_function

import os

from setuptools import find_packages, setup

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "swagger_spec_validator", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],

    description=about['__summary__'],

    url=about['__uri__'],

    author=about['__author__'],
    author_email=about['__email__'],
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        'swagger_spec_validator': [
            'swagger_spec_validator/schemas/v1.2/*',
            'swagger_spec_validator/schemas/v2.0/*',
        ],
    },
    include_package_data=True,
    install_requires=[
        'jsonref',
        'jsonschema',
        'setuptools',
        'six',
    ],
    license=about['__license__']
)
