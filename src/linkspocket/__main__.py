#!/usr/bin/env python3
# linkspocket is a tool to manage ootr settings and seeds in an OCI registry

from . import main
import sys

sys.exit(main(sys.argv[1:]))
