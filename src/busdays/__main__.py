"""Run the command line tool with ``python -m busdays``."""

from __future__ import annotations

import sys

from busdays._cli import main

if __name__ == "__main__":
    sys.exit(main())
