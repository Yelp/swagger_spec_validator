import logging
import string

import jsonref
import six

from swagger_spec_validator.common import (SwaggerValidationError,
                                           load_json,
                                           validate_json,
                                           wrap_exception)

log = logging.getLogger(__name__)


@wrap_exception
def validate_spec_url(spec_url):
    """Validates a Swagger 2.0 API Specification at the given URL.

    :param spec_url: the URL of the api-docs.
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    log.info('Validating %s' % spec_url)
    validate_spec(load_json(spec_url), spec_url)


def validate_spec(spec_json, spec_url=None):
    """Validates a Swagger 2.0 API Specification given a Swagger Spec.

    :param spec_json: the json dict of the swagger spec.
    :type spec_json: dict
    :param spec_url: url serving the spec json. Used for dereferencing
                     relative refs. eg: file:///foo/swagger.json
    :type spec_url: string
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    # Dereference all $refs so we don't have to deal with them
    fix_malformed_model_refs(spec_json)
    spec_json = jsonref.JsonRef.replace_refs(spec_json,
                                             base_uri=spec_url or '')
    replace_jsonref_proxies(spec_json)

    # Must validate after all refs in spec_json have been de-reffed because
    # jsonschema doesn't support validation of external refs
    validate_json(spec_json, 'schemas/v2.0/schema.json')

    apis = spec_json['paths']
    definitions = spec_json.get('definitions', {})
    validate_apis(apis)
    validate_definitions(definitions)


def validate_apis(apis):
    """Validates the semantic errors in `paths` of the Spec.

    :param apis: dict of all the paths
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    for api_name, api_body in six.iteritems(apis):
        api_params = api_body.get('parameters', [])
        validate_duplicate_param(api_params)
        for oper_name in api_body:
            # don't treat parameters that apply to all api operations as
            # an operation
            if oper_name == 'parameters':
                continue
            oper_body = api_body[oper_name]
            oper_params = oper_body.get('parameters', [])
            validate_duplicate_param(oper_params)
            all_path_params = list(set(get_path_param_names(api_params) +
                                       get_path_param_names(oper_params)))
            validate_unresolvable_path_params(api_name, all_path_params)


def validate_definitions(definitions):
    """Validates the semantic errors in `definitions` of the Spec.

    :param apis: dict of all the definitions
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    for def_name in definitions:
        definition = definitions[def_name]
        required = definition.get('required', [])
        props = definition.get('properties', {}).keys()
        extra_props = list(set(required) - set(props))
        msg = "Required list has properties not defined"
        if extra_props:
            raise SwaggerValidationError("%s: %s" % (msg, extra_props))


def get_path_param_names(params):
    """Fetch all the names of the path parameters of an operation

    :param params: list of all the params
    :returns: list of the name of the path params
    """
    return [param['name']
            for param in params
            if param['in'] == 'path']


def validate_duplicate_param(params):
    """Validate no duplicate parameters are present.
    Uniqueness is determined by the combination of 'name' and 'in'.

    :param params: list of all the params
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    seen = set()
    msg = "Duplicate param found with (name, in)"
    for param in params:
        param_id = (param['name'], param['in'])
        if param_id in seen:
            raise SwaggerValidationError("%s: %s" % (msg, param_id))
        seen.add(param_id)


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
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    msg = "Path Parameter used is not defined"
    for path in get_path_params_from_url(path_name):
        if path not in path_params:
            raise SwaggerValidationError("%s: %s" % (msg, path))


def replace_jsonref_proxies(obj):
    """
    Replace jsonref proxies in the given json obj with the proxy target.
    Updates are made in place. This removes compatibility problems with 3rd
    party libraries that can't handle jsonref proxy objects.

    :param obj: json like object
    :type obj: int, bool, string, float, list, dict, etc
    """
    # See https://github.com/gazpachoking/jsonref/issues/9
    def descend(fragment):
        if isinstance(fragment, dict):
            for k, v in six.iteritems(fragment):
                if isinstance(v, jsonref.JsonRef):
                    fragment[k] = v.__subject__
                descend(fragment[k])
        elif isinstance(fragment, list):
            for index, element in enumerate(fragment):
                if isinstance(element, jsonref.JsonRef):
                    fragment[index] = element.__subject__
                descend(element)

    descend(obj)


def fix_malformed_model_refs(spec):
    """jsonref doesn't understand  { $ref: Category } so just fix it up to
    { $ref: #/definitions/Category } when the ref name matches a #/definitions
    name. Yes, this is hacky!

    :param spec: Swagger spec in dict form
    """
    # Copied from https://github.com/Yelp/bravado-core/blob/v1.1.0/bravado_core/model.py#L166
    model_names = [model_name for model_name in spec.get('definitions', {})]

    def descend(fragment):
        if isinstance(fragment, dict):
            for k, v in six.iteritems(fragment):
                if k == '$ref' and v in model_names:
                    fragment[k] = "#/definitions/{0}".format(v)
                descend(v)
        elif isinstance(fragment, list):
            for element in fragment:
                descend(element)

    descend(spec)
