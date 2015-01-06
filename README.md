# swagger_spec_validator

## About

Swagger Spec Validator is a Python library that validates *Swagger Specs* against the `Swagger 1.2`_ or `Swagger 2.0`_ specification.  The validator aims to check for full compliance with the Specification.

## Example Usage

    import swagger_spec_validator

    swagger_spec_validator.validate_resource_listing_url('http://petstore.swagger.wordnik.com/api/api-docs')

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

