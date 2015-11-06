import contextlib
import sys

try:
    import simplejson as json
except ImportError:
    import json
from jsonschema import RefResolver
from jsonschema.validators import Draft4Validator
from pkg_resources import resource_filename
import six
from six.moves.urllib import request

from swagger_spec_validator import ref_validators

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


@wrap_exception
def validate_json(spec_dict, schema_path, spec_url=''):
    """Validate a json document against a json schema.

    :param spec_dict: json document in the form of a list or dict.
    :param schema_path: package relative path of the json schema file.
    :param spec_url: base uri to use when creating a
        RefResolver for the passed in spec_dict.

    :return: spec_dict resolver used during validation
    :rtype: :class:`jsonschema.RefResolver`
    """
    schema_path = resource_filename('swagger_spec_validator', schema_path)
    with open(schema_path) as schema_file:
        schema = json.loads(schema_file.read())

    schema_resolver = RefResolver('file://{0}'.format(schema_path), schema)
    spec_resolver = RefResolver(spec_url, spec_dict)

    ref_validators.ssv_validate(
        spec_dict,
        schema,
        resolver=schema_resolver,
        instance_cls=ref_validators.create_dereffing_validator(spec_resolver),
        cls=Draft4Validator)

    # Since remote $refs were downloaded, pass the resolver back to the caller
    # so that its cached $refs can be re-used.
    return spec_resolver


def load_json(url):
    with contextlib.closing(request.urlopen(url, timeout=TIMEOUT_SEC)) as fh:
        return json.loads(fh.read().decode('utf-8'))


class SwaggerValidationError(Exception):
    """Exception raised in case of a validation error."""
    pass
