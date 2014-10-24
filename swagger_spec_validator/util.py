import json
import logging
import urllib2

from .validator import validate_resource_listing
from .validator import validate_api_declaration


log = logging.getLogger(__name__)


def validate_resource_listing_url(url):
    """Simple utility function to perform recursive validation of a Resource
    Listing and all associated API Declarations.

    This is trivial wrapper function around
    :py:func:`swagger_spec_validator.validate_resource_listing` and
    :py:func:`swagger_spec_validator.validate_api_declaration`.  You are
    encouraged to write your own version of this if required.

    :param url: the URL of the Resource Listing.

    :returns: `None` in case of success, otherwise raises an exception.

    :raises: :py:class:`swagger_spec_validator.SwaggerValidationError`
    :raises: :py:class:`jsonschema.exceptions.ValidationError`
    """

    log.info('Validating %s' % url)
    resource_listing = json.load(urllib2.urlopen(url, timeout=1))
    validate_resource_listing(resource_listing)

    for api in resource_listing['apis']:
        path = url + api['path']
        log.info('Validating %s' % path)
        api_declaration = json.load(urllib2.urlopen(path, timeout=1))
        validate_api_declaration(api_declaration)
