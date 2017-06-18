from __future__ import absolute_import, division, print_function

import os

import sys
from setuptools import find_packages, setup

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "swagger_spec_validator", "__about__.py")) as f:
    exec(f.read(), about)


has_enum = sys.version_info >= (3, 4)

install_requires = [
    'jsonschema',
    'pyyaml',
    'six',
]

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
    install_requires=install_requires if has_enum else (install_requires + ['enum34']),
    license=about['__license__'],
)
