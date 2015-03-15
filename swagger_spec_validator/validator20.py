import logging
import string
import urllib2

from swagger_spec_validator.common import (SwaggerValidationError,
                                           TIMEOUT_SEC,
                                           json,
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
    spec_json = json.load(urllib2.urlopen(spec_url, timeout=TIMEOUT_SEC))
    validate_spec(spec_json)


def validate_spec(spec_json, _spec_url=None):
    """Validates a Swagger 2.0 API Specification given a Swagger Spec.

    :param spec_json: the json dict of the swagger spec.
    :type spec_json: dict
    :param _spec_url: url serving the spec json (currently not used)
    :type _spec_url: string
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    """
    validate_json(spec_json, 'schemas/v2.0/schema.json')

    # TODO: Extract 'parameters', 'responses' from the spec as well.
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
    for api_name, api_body in apis.iteritems():
        api_params = api_body.get('parameters', [])
        validate_duplicate_param(api_params)
        for oper_name in api_body:
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
