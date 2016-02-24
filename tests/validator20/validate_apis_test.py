from swagger_spec_validator.validator20 import validate_apis


def test_api_level_params_ok():
    # Parameters defined at the API level apply to all operations within that
    # API. Make sure we don't treat the API level parameters as an operation
    # since they are peers.
    apis = {
        '/tags/{tag-name}': {
            'parameters': [
                {
                    'name': 'tag-name',
                    'in': 'path',
                    'type': 'string',
                },
            ],
            'get': {
            }
        }
    }
    # Success == no exception thrown
    validate_apis(apis, lambda x: x)


def test_api_level_x_hyphen_ok():
    # Elements starting with "x-" should be ignored
    apis = {
        '/tags/{tag-name}': {
            'x-ignore-me': 'DO NOT LOOK AT ME!',
            'get': {
                'parameters': [
                    {
                        'name': 'tag-name',
                        'in': 'path',
                        'type': 'string',
                    }
                ]
            }
        }
    }
    # Success == no exception thrown
    validate_apis(apis, lambda x: x)
