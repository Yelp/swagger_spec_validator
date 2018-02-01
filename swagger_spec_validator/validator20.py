# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
import logging
import string

from jsonschema.validators import Draft4Validator
from jsonschema.validators import RefResolver
from pkg_resources import resource_filename
from six import iteritems
from six import iterkeys

from swagger_spec_validator import ref_validators
from swagger_spec_validator.common import read_file
from swagger_spec_validator.common import read_url
from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.common import wrap_exception
from swagger_spec_validator.ref_validators import default_handlers
from swagger_spec_validator.ref_validators import in_scope
from swagger_spec_validator.ref_validators import validate_schema_value


log = logging.getLogger(__name__)


def deref(ref_dict, resolver):
    """Dereference ref_dict (if it is indeed a ref) and return what the
    ref points to.

    :param ref_dict: Something like {'$ref': '#/blah/blah'}
    :type ref_dict: dict
    :param resolver: Ref resolver used to do the de-referencing
    :type resolver: :class:`jsonschema.RefResolver`

    :return: de-referenced value of ref_dict
    :rtype: scalar, list, dict
    """
    if ref_dict is None or not is_ref(ref_dict):
        return ref_dict

    ref = ref_dict['$ref']
    with in_scope(resolver, ref_dict):
        with resolver.resolving(ref) as target:
            log.debug('Resolving %s', ref)
            return target


@wrap_exception
def validate_spec_url(spec_url):
    """Validates a Swagger 2.0 API Specification at the given URL.

    :param spec_url: the URL of the service's swagger spec.

    :returns: The resolver (with cached remote refs) used during validation
    :rtype: :class:`jsonschema.RefResolver`
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    log.info('Validating %s', spec_url)
    return validate_spec(read_url(spec_url), spec_url)


def validate_spec(spec_dict, spec_url='',
                  http_handlers=None, custom_handlers=None,
                  apis_getter=None, definitions_getter=None,
                  apis_validator=None, definitions_validator=None,
                  schema_dict=None, urljoin_cache=None):
    """Validates a Swagger 2.0 API Specification given a Swagger Spec.

    :param spec_dict: the json dict of the swagger spec.
    :type spec_dict: dict
    :param spec_url: url from which spec_dict was retrieved. Used for
        dereferencing refs. eg: file:///foo/swagger.json
    :type spec_url: string
    :param http_handlers: deprecated. use the 'custom_handlers' parameter
        instead
    :param custom_handlers: used to download any remote $refs in spec_dict
        with a custom http client or used to add custom handlers for $refs.
        Defaults to None in which case the default http client built into
        jsonschema's RefResolver is used. This is a mapping from uri scheme
        to a callable that takes a uri.
    :param apis_getter: a callable used to get the apis from the 'paths'
        object.
    :param definitions_getter: a callable used to get the definitions from
        the 'definitions' object.
    :param apis_validator: a callable used to validate the apis specification.
    :param definitions_validator: a callable used to validate the definitions
        specification.
    :param schema_dict: the schema which validate the swagger specification.
    :param urljoin_cache: a callable to be used on the
        `jsonschema.RefResolver` constructor.

    :returns: the resolver (with cached remote refs) used during validation
    :rtype: :class:`jsonschema.RefResolver`
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    def default_getter(obj, deref):
        return deref(obj)

    if custom_handlers is None:
        custom_handlers = http_handlers

    swagger_resolver = validate_json(
        spec_dict,
        'schemas/v2.0/schema.json',
        spec_url=spec_url,
        custom_handlers=custom_handlers,
        schema=schema_dict,
        urljoin_cache=urljoin_cache)

    apis_getter = apis_getter or default_getter
    definitions_getter = definitions_getter or default_getter
    apis_validator = apis_validator or validate_apis
    definitions_validator = definitions_validator or validate_definitions

    bound_deref = functools.partial(deref, resolver=swagger_resolver)

    spec_dict = bound_deref(spec_dict)
    apis = apis_getter(spec_dict['paths'], bound_deref)
    definitions = definitions_getter(spec_dict.get('definitions', {}),
                                     bound_deref)

    apis_validator(apis, bound_deref)
    definitions_validator(definitions, bound_deref)
    return swagger_resolver


@wrap_exception
def validate_json(spec_dict, schema_path, spec_url='',
                  http_handlers=None, custom_handlers=None,
                  schema=None, urljoin_cache=None):
    """Validate a json document against a json schema.

    :param spec_dict: json document in the form of a list or dict.
    :param schema_path: package relative path of the json schema file.
    :param spec_url: base uri to use when creating a
        RefResolver for the passed in spec_dict.
    :param http_handlers: deprecated. use the 'custom_handlers' parameter
        instead
    :param custom_handlers: used to download any remote $refs in spec_dict
        with a custom http client or used to add custom handlers for $refs.
        Defaults to None in which case the default http client built into
        jsonschema's RefResolver is used. This is a mapping from uri scheme
        to a callable that takes a uri.
    :param schema: the schema which validate the swagger specification.
    :type schema: dict | None
    :param urljoin_cache: a callable to be used on the
        `jsonschema.RefResolver` constructor.

    :return: RefResolver for spec_dict with cached remote $refs used during
        validation.
    :rtype: :class:`jsonschema.RefResolver`
    """
    if custom_handlers is None:
        custom_handlers = http_handlers

    if schema is None:
        schema_path = resource_filename('swagger_spec_validator', schema_path)
        schema = read_file(schema_path)

    schema_resolver = RefResolver(
        base_uri='file://{}'.format(schema_path),
        referrer=schema,
        handlers=custom_handlers or default_handlers,
        urljoin_cache=urljoin_cache
    )

    spec_resolver = RefResolver(
        base_uri=spec_url,
        referrer=spec_dict,
        handlers=custom_handlers or default_handlers,
        urljoin_cache=urljoin_cache
    )

    ref_validators.validate(
        instance=spec_dict,
        schema=schema,
        resolver=schema_resolver,
        instance_cls=ref_validators.create_dereffing_validator(spec_resolver),
        cls=Draft4Validator,
    )

    # Since remote $refs were downloaded, pass the resolver back to the caller
    # so that its cached $refs can be re-used.
    return spec_resolver


@wrap_exception
def validate_value_type(schema, value, deref):
    # Extract resolver from deref partial build on ``validate_spec``
    # This is used in order to use already fetched external references
    # If it is missing a new RefResolver will be initialized
    swagger_resolver = getattr(deref, 'keywords', {}).get('resolver', None)
    validate_schema_value(schema=deref(schema), value=value, swagger_resolver=swagger_resolver)


def validate_defaults_in_parameters(params_spec, deref):
    """
    Validates that default values for api parameters are
    of the parameter type

    :param params_spec: list of parameter objects (#/paths/<path>/<http_verb>/parameters)
    :param deref: callable that dereferences $refs

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    for param_spec in params_spec:
        deref_param_spec = deref(param_spec)
        if deref_param_spec.get('required', False):
            # If the parameter is a required parameter, default has no meaning
            continue

        if 'default' in deref_param_spec:
            validate_value_type(
                schema=deref_param_spec,
                value=deref_param_spec['default'],
                deref=deref,
            )


def validate_apis(apis, deref):
    """Validates semantic errors in #/paths.

    :param apis: dict of all the #/paths
    :param deref: callable that dereferences $refs

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    for api_name, api_body in iteritems(apis):
        api_body = deref(api_body)
        api_params = deref(api_body.get('parameters', []))
        validate_duplicate_param(api_params, deref)
        for oper_name in api_body:
            # don't treat parameters that apply to all api operations as
            # an operation
            if oper_name == 'parameters' or oper_name.startswith('x-'):
                continue
            oper_body = deref(api_body[oper_name])
            oper_params = deref(oper_body.get('parameters', []))
            validate_duplicate_param(oper_params, deref)
            all_path_params = list(set(
                get_path_param_names(api_params, deref) +
                get_path_param_names(oper_params, deref)))
            validate_unresolvable_path_params(api_name, all_path_params)
            validate_defaults_in_parameters(oper_params, deref)


def get_collapsed_properties_type_mappings(definition, deref):
    """
    Get all the properties for a swagger model (definition).
    :param definition: dictionary representation of the definition
    :type definition: dict
    :param deref: callable that dereferences $refs
    :return: (required properties type mapping, not required properties type mapping)
    :type: tuple
    """
    definition = deref(definition)
    required_properties = {}
    not_required_properties = {}
    if definition.get('allOf'):
        for inner_definition in definition['allOf']:
            inner_required_properties, inner_not_required_properties = get_collapsed_properties_type_mappings(inner_definition, deref)
            required_properties.update(inner_required_properties)
            not_required_properties.update(inner_not_required_properties)
    else:
        properties = {
            prop_name: prop_schema.get('type', 'object')
            for prop_name, prop_schema in iteritems(definition.get('properties', {}))
        }
        required_properties_set = set(definition.get('required', []))
        for k, v in iteritems(properties):
            if k in required_properties_set:
                required_properties[k] = v
            else:
                not_required_properties[k] = v

    return required_properties, not_required_properties


def validate_property_default(property_spec, deref):
    """
    Validates that default values for definitions are of the property type.
    Enforces presence of "type" in case of "default" presence.

    :param property_spec: schema object (#/definitions/<def_name>/properties/<property_name>
    :param deref: callable that dereferences $refs

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    deref_property_spec = deref(property_spec)
    if 'default' in deref_property_spec:
        validate_value_type(schema=property_spec, value=deref_property_spec['default'], deref=deref)


def validate_defaults_in_definition(definition_spec, deref):
    for property_name, property_spec in iteritems(definition_spec.get('properties', {})):
        validate_property_default(property_spec, deref)


def validate_definition(definition, deref, def_name=None):
    definition = deref(definition)

    if 'allOf' in definition:
        for inner_definition in definition['allOf']:
            validate_definition(inner_definition, deref)
    else:
        required = definition.get('required', [])
        props = iterkeys(definition.get('properties', {}))
        extra_props = list(set(required) - set(props))
        if extra_props:
            raise SwaggerValidationError(
                "Required list has properties not defined: {}".format(
                    extra_props
                )
            )

        validate_defaults_in_definition(definition, deref)

    if 'discriminator' in definition:
        required_props, not_required_props = get_collapsed_properties_type_mappings(definition, deref)
        discriminator = definition['discriminator']
        if discriminator not in required_props and discriminator not in not_required_props:
            raise SwaggerValidationError('discriminator (%s) must be defined in properties' % discriminator)
        if discriminator not in required_props:
            raise SwaggerValidationError('discriminator (%s) must be defined a required property' % discriminator)
        if required_props[discriminator] != 'string':
            raise SwaggerValidationError('discriminator (%s) must be a string property' % discriminator)


def validate_definitions(definitions, deref):
    """Validates the semantic errors in #/definitions.

    :param definitions: dict of all the definitions
    :param deref: callable that dereferences $refs

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    for def_name, definition in iteritems(definitions):
        validate_definition(definition, deref, def_name=def_name)


def get_path_param_names(params, deref):
    """Fetch all the names of the path parameters of an operation.

    :param params: list of all the params
    :param deref: callable that dereferences $refs

    :returns: list of the name of the path params
    """
    return [
        deref(param)['name']
        for param in params
        if deref(param)['in'] == 'path'
    ]


def validate_duplicate_param(params, deref):
    """Validate no duplicate parameters are present.

    Uniqueness is determined by the tuple ('name', 'in').

    :param params: list of all the params
    :param deref: callable that dereferences $refs

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError` when
        a duplicate parameter is found.
    """
    seen = set()
    msg = "Duplicate param found with (name, in)"
    for param in params:
        param = deref(param)
        param_key = (param['name'], param['in'])
        if param_key in seen:
            raise SwaggerValidationError("%s: %s" % (msg, param_key))
        seen.add(param_key)


def get_path_params_from_url(path):
    """Parse the path parameters from a path string

    :param path: path url to parse for parameters

    :returns: List of path parameter names
    """
    formatter = string.Formatter()
    path_params = [item[1] for item in formatter.parse(path)]
    return filter(None, path_params)


def validate_unresolvable_path_params(path_name, path_params):
    """Validate that every path parameter listed is also defined.

    :param path_name: complete path name as a string.
    :param path_params: Names of all the eligible path parameters

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    for path in get_path_params_from_url(path_name):
        if path not in path_params:
            msg = "Path parameter '{}' used is not documented on '{}'".format(path, path_name)
            raise SwaggerValidationError(msg)


def is_ref(spec_dict):
    return isinstance(spec_dict, dict) and '$ref' in spec_dict
