# -*- coding: utf-8 -*-
import contextlib
import sys

from yaml import safe_load


import six
from six.moves.urllib import request
from six.moves.urllib.parse import urlparse
from jsonschema.compat import urlopen


TIMEOUT_SEC = 1


def wrap_exception(method):
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            six.reraise(
                SwaggerValidationError,
                SwaggerValidationError(str(e)),
                sys.exc_info()[2])
    return wrapper


def read_file(file_path):
    """
    Utility method for reading a JSON/YAML file and converting it to a Python dictionary
    :param file_path: path of the file to read

    :return: Python dictionary representation of the JSON file
    :rtype: dict
    """
    with open(file_path) as f:
        # NOTE: JSON is a subset of YAML so it is safe to read JSON as it is YAML
        return safe_load(f)


def read_url(url):
    if urlparse(url).scheme == 'file':
        fp = urlopen(url)
        return safe_load(fp)
    else:
        with contextlib.closing(request.urlopen(url, timeout=TIMEOUT_SEC)) as fh:
            # NOTE: JSON is a subset of YAML so it is safe to read JSON as it is YAML
            return safe_load(fh.read().decode('utf-8'))


class SwaggerValidationError(Exception):
    """Exception raised in case of a validation error."""
    pass
