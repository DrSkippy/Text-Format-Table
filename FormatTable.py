#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Backwards-compatible import path for :class:`text_format_table.FormatTable`."""

from text_format_table.format_table import FormatTable

__all__ = ["FormatTable"]

if __name__ == "__main__":
    from text_format_table.demo import format_table_demo

    format_table_demo()
