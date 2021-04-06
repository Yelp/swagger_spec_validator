# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys

from setuptools import find_packages, setup

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "swagger_spec_validator", "__about__.py")) as f:
    exec(f.read(), about)


install_requires = [
    'jsonschema',
    'pyyaml',
    'six',
]

if sys.version_info <= (3, 0):
    install_requires.append('pyrsistent<0.17.0')

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
    install_requires=install_requires,
    extra_dependencies={'python_version<"3"': ["functools32"]},
    license=about['__license__'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
    ],
)
