import json
import logging
import urllib2

from swagger_spec_validator import validator12, validator20
from swagger_spec_validator.common import SwaggerValidationError


log = logging.getLogger(__name__)

version_to_validator = {
    '1.2': validator12,
    '2.0': validator20,
}


def get_validator(spec_json, origin):
    """
    :param spec_json: Dict representation of the API spec
    :param origin: filename or url of the spec
    :return: module responsible for validation based on swaggerVersion
    """
    swagger_version = spec_json.get('swaggerVersion')

    if swagger_version is None:
        raise SwaggerValidationError(
            "Swagger spec {0} is missing swaggerVersion".format(origin))

    validator = version_to_validator.get(swagger_version)

    if validator is None:
        raise SwaggerValidationError(
            'Swagger version {0} in {1} is not supported'.format(
                swagger_version, origin))

    return validator


def validate_spec_url(spec_url):
    """Validates a Swagger spec given its URL.

    :param spec_url:
      For Swagger 1.2, this is the URL to the resource listing in api-docs.
      For Swagger 2.0, this is the URL to swagger.json in api-docs.
    """
    spec_json = json.load(urllib2.urlopen(spec_url, timeout=1))
    validator = get_validator(spec_json, spec_url)
    validator.validate_spec_url(spec_url)
