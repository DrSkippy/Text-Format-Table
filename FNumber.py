#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Backwards-compatible import path for :class:`text_format_table.FNumber`."""

from text_format_table.fnumber import FNumber

__all__ = ["FNumber"]

if __name__ == "__main__":
    from text_format_table.demo import fnumber_demo

    fnumber_demo()
