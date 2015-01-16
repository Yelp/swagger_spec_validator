# swagger_spec_validator
[![Build Status](https://travis-ci.org/Yelp/swagger_spec_validator.svg?branch=master)](https://travis-ci.org/Yelp/swagger_spec_validator) 
[![Coverage Status](https://coveralls.io/repos/Yelp/swagger_spec_validator/badge.svg)](https://coveralls.io/r/Yelp/swagger_spec_validator)
[![Latest Version](https://pypip.in/version/swagger_spec_validator/badge.svg)](https://pypi.python.org/pypi/swagger_spec_validator/)

## About

Swagger Spec Validator is a Python library that validates Swagger Specs against the [Swagger 1.2](https://github.com/swagger-api/swagger-spec/blob/master/versions/1.2.md) or [Swagger 2.0](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md) specification.  The validator aims to check for full compliance with the Specification.

## Example Usage

    # 1.2 spec
    from swagger_spec_validator import validate_resource_listing_url
    validate_resource_listing_url('http://petstore.swagger.wordnik.com/api/api-docs')

    # 2.0 spec
    TBD

## Documentation

More documentation is available at http://swagger_spec_validator.readthedocs.org

## Installation

    $ pip install --upgrade git+git://github.com/Yelp/swagger_spec_validator

## Contributing

1. Fork it ( http://github.com/Yelp/swagger_spec_validator/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## License

Copyright (c) 2015, Yelp, Inc. All rights reserved.
Apache v2
