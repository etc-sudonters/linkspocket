#!/usr/bin/env python3
# linkspocket is a tool to manage ootr settings and seeds in an OCI registry

from . import main, cli
import sys

parser = cli.parser()
code = main(parser.parse_args())
if code != 0:
    parser.print_help()
sys.exit(code)
