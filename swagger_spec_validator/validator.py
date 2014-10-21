# -*- coding: utf-8 -*-

# Validate Swagger Specs against the Swagger 1.2 Specification.  The
# validator aims to check for full compliance with the Specification.
#
# The validator uses the published jsonschema files for basic structural
# validation, augmented with custom validation code where necessary.
#
# https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md

import json

import jsonschema
from jsonschema.validators import RefResolver
from pkg_resources import resource_filename


# Primitives (§4.3.1)
PRIMITIVE_TYPES = ['integer', 'number', 'string', 'boolean']


class SwaggerValidationError(Exception):
    """Exception raised in case of a validation error."""

    pass


def validate_jsonschema(schema_name, value):
    schema_path = resource_filename('swagger_spec_validator', 'schemas/v1.2/' + schema_name)
    with open(schema_path) as schema_file:
        schema = json.loads(schema_file.read())
    resolver = RefResolver('file://{0}'.format(schema_path), schema)
    jsonschema.validate(value, schema, resolver=resolver)


def get_model_ids(api_declaration):
    models = api_declaration.get('models', {})
    model_ids = []
    for model in models.itervalues():
        model_ids.append(model['id'])
    return model_ids


def validate_data_type(obj, model_ids, allow_arrays=True, allow_voids=False,
                       allow_refs=True):
    """Validate an object that contains a data type (§4.3.3).

    Params:
    - obj: the dictionary containing the data type to validate
    - model_ids: a list of model ids
    - allow_arrays: whether an array is permitted in the data type.  This is
      used to prevent nested arrays.
    - allow_voids: whether a void type is permitted.  This is used when
      validating Operation Objects (§5.2.3).
    - allow_refs: whether '$ref's are permitted.  If true, then 'type's
      are not allowed to reference model IDs.
    """

    typ = obj.get('type')
    ref = obj.get('$ref')

    # TODO Validate defaultValue, enum, minimum, maximum, uniqueItems
    if typ is not None:
        if typ in PRIMITIVE_TYPES:
            pass
        elif allow_voids and typ == 'void':
            pass
        elif typ == 'array':
            if not allow_arrays:
                raise SwaggerValidationError('"array" not allowed')
            # Items Object (§4.3.4)
            items = obj.get('items')
            if items is None:
                raise SwaggerValidationError('"items" not found')
            validate_data_type(items, model_ids, allow_arrays=False)
        elif typ in model_ids:
            if allow_refs:
                raise SwaggerValidationError('must use "$ref" for referencing "%s"' % typ)
        else:
            raise SwaggerValidationError('unknown type "%s"' % typ)
    elif ref is not None:
        if not allow_refs:
            raise SwaggerValidationError('"$ref" not allowed')
        if ref not in model_ids:
            raise SwaggerValidationError('unknown model id "%s"' % ref)
    else:
        raise SwaggerValidationError('no "$ref" or "type" present')


def validate_model(model, model_name, model_ids):
    """Validate a Model Object (§5.2.7)."""
    # TODO Validate 'sub-types' and 'discriminator' fields
    for required in model.get('required', []):
        if required not in model['properties']:
            raise SwaggerValidationError(
                'Model "%s": required property "%s" not found' %
                (model_name, required))

    for prop_name, prop in model.get('properties', {}).iteritems():
        try:
            validate_data_type(prop, model_ids, allow_refs=True)
        except SwaggerValidationError as e:
            # Add more context to the exception and re-raise
            raise SwaggerValidationError(
                'Model "%s", property "%s": %s' % (model_name, prop_name, str(e)))


def validate_parameter(parameter, model_ids):
    """Validate a Parameter Object (§5.2.4)."""
    validate_data_type(parameter, model_ids, allow_refs=False)


def validate_operation(operation, model_ids):
    """Validate an Operation Object (§5.2.3)."""
    try:
        validate_data_type(operation, model_ids, allow_refs=False, allow_voids=True)
    except SwaggerValidationError as e:
        raise SwaggerValidationError(
            'Operation "%s": %s' % (operation['nickname'], str(e)))

    for parameter in operation['parameters']:
        try:
            validate_parameter(parameter, model_ids)
        except SwaggerValidationError as e:
            raise SwaggerValidationError(
                'Operation "%s", parameter "%s": %s' %
                (operation['nickname'], parameter['name'], str(e)))


def validate_api(api, model_ids):
    """Validate an API Object (§5.2.2)."""
    for operation in api['operations']:
        validate_operation(operation, model_ids)


def validate_api_declaration(api_declaration):
    """Validate an API Declaration (§5.2).

    :param api_declaration: a dictionary respresentation of an API Declaration.

    :returns: `None` in case of success, otherwise raises an exception.

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    validate_jsonschema('apiDeclaration.json', api_declaration)

    model_ids = get_model_ids(api_declaration)

    for api in api_declaration['apis']:
        validate_api(api, model_ids)

    for model_name, model in api_declaration.get('models', {}).iteritems():
        validate_model(model, model_name, model_ids)


def validate_resource_listing(resource_listing):
    """Validate a Resource Listing (§5.1).

    :param resource_listing: a dictionary respresentation of a Resource Listing.

    Note that you will have to invoke `validate_api_declaration` on each
    linked API Declaration.

    :returns: `None` in case of success, otherwise raises an exception.

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    validate_jsonschema('resourceListing.json', resource_listing)
