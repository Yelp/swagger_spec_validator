import json
import logging
import urllib2

from swagger_spec_validator.common import validate_json

log = logging.getLogger(__name__)


def validate_spec_url(spec_url):
    """Validates a Swagger 2.0 API Specification at the given URL.

    :param spec_url: the URL of the api-docs.
    :returns: `None` in case of success, otherwise raises an exception.
    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """
    log.info('Validating %s' % spec_url)
    spec_json = json.load(urllib2.urlopen(spec_url, timeout=1))
    validate_spec(spec_json)


def validate_spec(spec_json):
    validate_json(spec_json, 'schemas/v2.0/schema.json')
    # TODO: rich schema validation
