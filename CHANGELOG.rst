Changelog
=========
3.0.1 (2022-10-19)
------------------
- Add py.typed marker - PR #158
- Enforce python_requires>=3.7

3.0.0 (2022-10-19)
------------------
- Add type annotations - PR #157
- Drop py2 and py36 support - PR #157
- Drop simplejson - PR #157

2.7.4 (2021-10-08)
------------------
- Make checks for unique operation ids global instead of per tag - PR #145

2.7.3 (2020-06-25)
------------------
- Fix recursive ref resolution for some specs split across multiple files - PR #140

2.7.2 (2020-06-10)
------------------
- Fix recursive definition detection - PR #139

2.7.1 (2020-06-09)
------------------
- Fix: `additionalProperties` can be a boolean value  - PR #138

2.7.0 (2020-06-05)
------------------
- Ensure correct validation into additionalProperties and items specifications - PR #134. Thanks brycedrennan for your contribution.

2.6.0 (2020-05-20)
------------------
- Improve validation performance in case of consecutive validations. - PR #132. Thanks brycedrennan for your contribution.

2.5.0 (2020-02-25)
------------------
- Use ``yaml.CSafeLoader`` if available - PR #122
- Show definition name when raising ``SwaggerValidationError`` - PR #124

2.4.3 (2019-01-16)
------------------
- Fix regression, introduced by PR #111, that was causing descending references with no scope. - PR #113

2.4.2 (2019-01-15)
------------------
- Add warning when ``$ref`` is defined to have ``None`` value - PR #111
- Ensure that only valid references (``$ref`` attribute is present with string value) are dereferenced - PR #111

2.4.1 (2018-10-09)
------------------
- Add warning when using ``$ref`` together with other properties - PR #107

2.4.0 (2018-08-28)
------------------
- Disallow multiple types in schema definitions. See `OpenAPI#458 <https://github.com/OAI/OpenAPI-Specification/issues/458>`_ for context - PR #106

2.3.1 (2018-06-11)
------------------
- Fix urlopen issue on Windows platform. Issue #99, PR #101

2.3.0 (2018-06-06)
------------------
- Ensure that inline models are validated - #97
- Ensure that parameters are validated - #97
- Validation of defaults set to None is skipped if x-nullable is set - #97

2.2.0 (2018-06-05)
------------------
- Add support for reading YAML files - #74
- Make sure operationIds are unique within the same tag - #93
- Validate that array models in the top-level definitions have an ``items`` property (validation for array models in other places will come in a future release) - #95
- Responses (the mapping of HTTP status codes to Response objects) cannot be a reference - #92
- ``$ref`` values need to be strings - #83. Thanks ceridwen for your contribution!
- Ensure that default values are compliant with the spec - #82
- More helpful error message when encountering unresolvable path params - #72. Thanks daym for your contribution!

2.1.0 (2017-03-21)
------------------
- Properly validate polymorphic objects - #68

2.0.4 (2017-03-10)
------------------
- Rename package to swagger-spec-validator to fix PyPI upload issues - #59

2.0.3 (2016-11-23)
------------------
- Ignore x- vendor extensions in the schema at the #/paths/{path}/{http_method} level - PR #45
- Swagger 2.0 schema synced with upstream - PR #40

2.0.2 (2015-11-18)
------------------
- Fix regression with Swagger 1.2 schemas - #43

2.0.1 (2015-11-17)
------------------
- Fix rich validations that rely on a working deref with scope annotations

2.0.0 (2015-11-17)
------------------
- Support for recursive $refs
- Unqualified $refs no longer supported.
  Bad:  ``{"$ref": "User"}``
  Good: ``{"$ref": "#/definitions/User"}``

1.1.1 (2015-10-02)
------------------
 - Workaround for validation of Swagger 2.0 schemas with external refs - #38

1.1.0 (2015-08-24)
------------------
 - Validate crossrefs - #33, #34

1.0.12 (2015-07-02)
-------------------
 - Handle API level parameters - #29
 - More robust handling of $refs - #29

1.0.11 (2015-06-02)
-------------------
 - Validation for model name and it (Swagger 1.2)
 - Remove unnecessary dependency on pyyaml

1.0.10 (2015-04-15)
-------------------
 - Pin of jsonschema used for unit tests for Python3

1.0.9 (2015-03-26)
------------------
 - Sync Swagger 2.0 schema with upstream - allow empty arrays for parameter
 - Handle schemas with no definitions

1.0.8 (2015-03-11)
------------------
 - Petstore URLs updated
 - Support 'type: File' for (Swagger 1.2)

1.0.7 (2015-03-02)
------------------
 - Python3 support
 - Use simplejson when available

1.0.5 (2015-02-19)
------------------
 - Add file:// support

1.0.3 (2015-01-05)
------------------
 - Initial support for Swagger 2.0

1.0.2 (2014-10-24)
------------------
 - Bugfix for path construction in validate_resource_listing_url

1.0.1 (2014-10-24)
------------------
 - Bugfix to including jsonschema files

1.0.0 (2014-10-24)
------------------
 - Initial version
