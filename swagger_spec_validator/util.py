import logging

from enum import Enum
from six import iteritems

from jsonschema import RefResolver
from jsonschema.exceptions import ValidationError
from swagger_spec_validator import validator12
from swagger_spec_validator import validator20
from swagger_spec_validator import ref_validators
from swagger_spec_validator.common import read_file
from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.common import read_url
from swagger_spec_validator.common import wrap_exception

from pkg_resources import resource_filename


log = logging.getLogger(__name__)


def get_validator(spec_json, origin='unknown'):
    """
    :param spec_json: Dict representation of the json API spec
    :param origin: filename or url of the spec - only use for error messages
    :return: module responsible for validation based on Swagger version in the
        spec
    """
    swagger12_version = spec_json.get('swaggerVersion')
    swagger20_version = spec_json.get('swagger')

    if swagger12_version and swagger20_version:
        raise SwaggerValidationError(
            "You've got conflicting keys for the Swagger version in your spec. "
            "Expected `swaggerVersion` or `swagger`, but not both.")
    elif swagger12_version and swagger12_version == '1.2':
        # we don't care about versions prior to 1.2
        return validator12
    elif swagger20_version and swagger20_version == '2.0':
        return validator20
    elif swagger12_version is None and swagger20_version is None:
        raise SwaggerValidationError(
            "Swagger spec {0} missing version. Expected "
            "`swaggerVersion` or `swagger`".format(origin))
    else:
        raise SwaggerValidationError(
            'Swagger version {0} not supported.'.format(
                swagger12_version or swagger20_version))


@wrap_exception
def validate_spec_url(spec_url):
    """Validates a Swagger spec given its URL.

    :param spec_url:
      For Swagger 1.2, this is the URL to the resource listing in api-docs.
      For Swagger 2.0, this is the URL to swagger.json in api-docs. If given
                       as `file://` this must be an absolute url for
                       cross-refs to work correctly.
    """
    spec_json = read_url(spec_url)
    validator = get_validator(spec_json, spec_url)
    validator.validate_spec(spec_json, spec_url)


def _initialize_Swagger2dot0ObjectType(object_mapping_schema_path='schemas/v2.0/object_mappings.json'):
    """
    Initialize Swagger2dot0ObjectType Enum from Object Mapping configurations.

    :param object_mapping_schema_path: package relative path of the json schema file representing the object mappings.
    :return: Swagger2dot0ObjectType enum
    """
    object_mappings_abspath = resource_filename('swagger_spec_validator', object_mapping_schema_path)

    # Load object mappings from JSON config file
    object_mappings = read_file(object_mappings_abspath)

    object_mappings_resolver = RefResolver(
        base_uri='file://{0}'.format(object_mappings_abspath),
        referrer=object_mappings,
    )
    mappings = {}
    for name, json_ref in iteritems(object_mappings):
        _, schema = object_mappings_resolver.resolve(json_ref['$ref'])
        mappings[name] = schema

    return Enum('Swagger2dot0ObjectType', mappings)


Swagger2dot0ObjectType = _initialize_Swagger2dot0ObjectType()


def determine_swagger2dot0_object_type(object_dict, object_resolver=None, spec_url='', http_handlers=None, possible_types=None):
    """
    Determine the possible Swagger Object types for a given object dictionary representation.

    :param object_dict: swagger spec json dict to determine the type
    :type object_dict: dict
    :param object_resolver: swagger spec reference resolver (ie. return value of ``swagger_spec_validator.validator20.validate_spec``)
    :type  object_resolver: jsonschema.RefResolver
    :param spec_url: url from which spec_dict was retrieved. Used for dereferencing refs. eg: file:///foo/swagger.json
    :type spec_url: string
    :param http_handlers: used to download any remote $refs in spec_dict with
        a custom http client. Defaults to None in which case the default
        http client built into jsonschema's RefResolver is used. This
        is a mapping from uri scheme to a callable that takes a
        uri.
    :param possible_types: Swagger2dot0 types to iterate. If None is set all the possible types will be analyzed
    :type possible_types: iterable[Swagger2dot0]

    :return: Set of Swagger2dot0 types under which object_dict is valid
    :rtype: set[Swagger2dot0]
    """

    def is_valid(object_type):
        try:
            validator_cls = ref_validators.create_dereffing_validator(object_resolver)
            validator = validator_cls(
                object_type.value,  # JSON Specification of self SwaggerObjectType
                resolver=schema_resolver,
            )
            validator.validate(object_dict)
            return True
        except ValidationError:
            return False

    _schema_path = resource_filename('swagger_spec_validator', 'schemas/v2.0/schema.json')

    # Init schema resolver
    schema = read_file(_schema_path)
    schema_resolver = RefResolver(
        base_uri='file://{0}'.format(_schema_path),
        referrer=schema,
    )

    if not object_resolver:
        object_resolver = RefResolver(
            base_uri=spec_url,
            referrer=object_dict,
            handlers=http_handlers or {},
        )

    if possible_types is None:
        possible_types = set(Swagger2dot0ObjectType)
    else:
        possible_types = set(Swagger2dot0ObjectType).intersection(set(possible_types))

    return {
        swagger_object_type
        for swagger_object_type in possible_types
        if is_valid(object_type=swagger_object_type)
    }
