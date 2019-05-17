# -*- coding: utf-8 -*-
"""
Swagger spec validator.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import sys

from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.util import validate_spec_url


def _extract_error_message(exc):
    """
    The validators return nested errors coming from common.wrap_exception, so to
    present as a nice string to print we need to dig out the original message.
    """
    try:
        return exc.args[1].args[0]
    except IndexError:
        # not 100% sure it is *always* wrapped, but this should provide a
        # fallback.
        return str(exc)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]  # pragma: no cover

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("url", type=str, help="URL of Swagger spec to validate")
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="No output if validation is successful",
    )

    args = parser.parse_args(argv)

    try:
        validate_spec_url(args.url)
    except SwaggerValidationError as exc:
        error_message = _extract_error_message(exc)
        print(error_message, file=sys.stderr)
        return 1

    if not args.quiet:
        print("Validation successful!", file=sys.stderr)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
