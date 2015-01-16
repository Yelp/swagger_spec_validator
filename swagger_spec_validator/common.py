import json
from jsonschema import RefResolver
import jsonschema
from pkg_resources import resource_filename


def validate_json(json_document, schema_path):
    """Validate a json document against a json schema.

    :param json_document: json document in the form of a list or dict.
    :param schema_path: package relative path of the json schema file.
    """
    schema_path = resource_filename('swagger_spec_validator', schema_path)
    with open(schema_path) as schema_file:
        schema = json.loads(schema_file.read())
    resolver = RefResolver('file://{0}'.format(schema_path), schema)
    jsonschema.validate(json_document, schema, resolver=resolver)


class SwaggerValidationError(Exception):
    """Exception raised in case of a validation error."""
    pass
