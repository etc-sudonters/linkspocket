#!/usr/bin/env python3
# linkspocket is a tool to manage ootr settings and seeds in an OCI registry

import sys

from . import cli, main

parser = cli.parser()
if (code := main(parser.parse_args())) != 0:
    parser.print_help()
sys.exit(code)
