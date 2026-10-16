#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Backwards-compatible script; see :mod:`text_format_table.cli`.

Read a comma delimited file and output formatted text table.
Assumes header row is first.
"""

import sys

from text_format_table.cli import main

if __name__ == "__main__":
    sys.exit(main())
