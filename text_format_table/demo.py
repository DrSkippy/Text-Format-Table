# SPDX-License-Identifier: LGPL-3.0-or-later
"""Examples formerly in the ``__main__`` blocks of FNumber.py and FormatTable.py.

Run with ``python -m text_format_table.demo``.
"""

from __future__ import annotations

import sys

from text_format_table.exceptions import InvalidSignificantFiguresError
from text_format_table.fnumber import Cell, FNumber
from text_format_table.format_table import FormatTable

DEMO_COLUMN_WIDTH = 30
DEMO_COLUMN_OFFSET = 15
DEMO_CONSTANT_SIG_FIGS = 3

FNUMBER_VALUES: list[tuple[Cell, int]] = [
    (1234.234, 1),
    (1234.234, 2),
    (1234.234, 3),
    (123.234, 3),
    (123.234, 4),
    (1234.234, 4),
    (1234.234, 5),
    (-1234.234, 5),
    (1234.234, 6),
    (1234.234, 7),
    (1234.234, 9),
    (0.23456789, 1),
    (0.23456789, 2),
    ("hello there", 0),
    (-0.23456789, 2),
    (0.23456789, 3),
    (0.23456789, 4),
    (0.23456789, 5),
    (0.0023456789, 3),
    (0.00023456789, 4),
    (0.000023456789, 5),
    (23456789, 2),
    (23456789, 4),
    (23456789, 6),
    (-23456789, 6),
    (23456789.123345, 8),
    (23456789.123345, 11),
    (1234.234, 0),
]

TABLE_VALUES: list[list[tuple[Cell, int]]] = [
    [("column 1", 0), ("column 2", 0), ("column C", 0), ("another column", 0)],
    [(1234.234, 1), (1234.234, 2), (1234.234, 3), (123.234, 3)],
    [(123.234, 4), (1234.234, 1), (123.234, 4), (1234.234, 4)],
    [(1234.234, 5), (-1234.234, 5), (1234.234, 6), (1234.234, 7)],
    [(1234.234, 9), (0.23456789, 1), (0.23456789, 2), (-0.23456789, 2)],
    [(0.23456789, 3), (0.23456789, 4), (0.23456789, 5), (0.0023456789, 3)],
    [(0.00023456789, 4), (0.000023456789, 5), (23456789, 2), (23456789, 4)],
    [(23456789, 6), (-23456789, 6), (23456789.123345, 8), (23456789.123345, 15)],
]


def fnumber_demo() -> None:
    """Simple example of a single column of numbers, aligned on the decimal points.

    The final value requests 0 significant figures, which stops the demo with
    an error message on stderr.
    """
    for value, sig_figs in FNUMBER_VALUES:
        try:
            number = FNumber(value, sig_figs)
        except InvalidSignificantFiguresError as error:
            print(error, file=sys.stderr)
            return
        print(number.pad(DEMO_COLUMN_WIDTH, DEMO_COLUMN_OFFSET))


def format_table_demo() -> None:
    """Simple example of multi-column table with varying sf specified for each number."""
    print(FormatTable(TABLE_VALUES))
    print("*****\n")
    # ...and same numbers with constant sf for the whole table
    values_only = [[value for value, _ in row] for row in TABLE_VALUES]
    print(FormatTable(values_only, DEMO_CONSTANT_SIG_FIGS))
    print("*****\n")
    print(FormatTable(values_only, DEMO_CONSTANT_SIG_FIGS, latex=True))


if __name__ == "__main__":  # pragma: no cover
    fnumber_demo()
    format_table_demo()
