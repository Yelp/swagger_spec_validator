# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

from swagger_spec_validator.util import validate_spec_url


def main():
    parser = argparse.ArgumentParser()
    parser.description = 'Check specification against the Swagger standard'
    parser.add_argument('url', type=str)
    args = parser.parse_args()
    validate_spec_url(args.url)


if __name__ == '__main__':
    main()
