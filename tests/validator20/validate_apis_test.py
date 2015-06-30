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
    validate_apis(apis)
