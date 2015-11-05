import functools
import contextlib
import sys


try:
    import simplejson as json
except ImportError:
    import json
import jsonschema
from jsonschema import RefResolver
from jsonschema.compat import iteritems
from jsonschema.validators import Draft4Validator
from jsonschema import validators
from pkg_resources import resource_filename
import six
from six.moves.urllib import request

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

    jsonschema.validate(
        spec_dict,
        schema,
        resolver=schema_resolver,
        cls=create_ref_following_validator(spec_resolver))

    # Since remote $refs were downloaded, pass the resolver back to the caller
    # so that its cached $refs can be re-used.
    return spec_resolver


def create_ref_following_validator(instance_resolver):
    """Create a customized Draft4Validator that follows $refs in the schema
    being validated (the Swagger spec for a service). This is not to be
    confused $refs that are in the schema that describes the Swagger 2.0
    specification.

    :param instance_resolver: resolver for the swagger service's spec
    :type instance_resolver: :class:`jsonschema.RefResolver`

    :rtype: Its complicated. See jsonschema.validators.create()
    """
    return validators.extend(
        Draft4Validator,
        {
            # The instance_resolver is bound to validation function for
            # properties so that $refs can be resolved.
            'properties': functools.partial(
                ref_following_properties_draft4,
                instance_resolver=instance_resolver),
        })


def ref_following_properties_draft4(validator, properties, instance, schema,
                                    instance_resolver):
    """Custom 'properties' validator for Swagger 2.0 services that follows
    $ref's

    :type validator: :class:`jsonschema.validators.Validator`
    :param properties: dict of properties that are expected in the instance
    :param instance: fragment of the Swagger 2.0 service's spec that is being
        validated.
    :param schema: The schema for validating Swagger 2.0 specs
    :param instance_resolver: Resolver for the spec of the Swagger 2.0 service.
    :type instance_resolver: :class:`jsonschema.RefResolver'
    """
    if not validator.is_type(instance, "object"):
        return

    for property, subschema in iteritems(properties):
        if property in instance:
            if property != '$ref':
                for error in validator.descend(
                    instance[property],
                    subschema,
                    path=property,
                    schema_path=property,
                ):
                    yield error
            # The only new code in this method are the lines below. Lines
            # above copied from `jsonschema._validators.properties_draft4`.
            else:
                # Dereference the $ref and feed the target of the $ref back
                # into the properties validator as if the $ref never existed.
                ref = instance['$ref']
                # TODO: remove print
                print("De-reffing and following %s' % ref")
                with instance_resolver.resolving(ref) as target:
                    for error in ref_following_properties_draft4(
                            validator, properties, target, schema,
                            instance_resolver=instance_resolver):
                        yield error


def load_json(url):
    with contextlib.closing(request.urlopen(url, timeout=TIMEOUT_SEC)) as fh:
        return json.loads(fh.read().decode('utf-8'))


class SwaggerValidationError(Exception):
    """Exception raised in case of a validation error."""
    pass
