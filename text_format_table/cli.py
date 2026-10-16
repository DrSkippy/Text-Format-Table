# SPDX-License-Identifier: LGPL-3.0-or-later
"""Command line entry point.

Read a comma delimited file and output formatted text table.
Assumes header row is first.
"""

from __future__ import annotations

import argparse
import csv
import fileinput
import sys
from collections.abc import Sequence

from text_format_table.config import DEFAULT_CONFIG, FormatConfig, load_config
from text_format_table.exceptions import TextFormatTableError
from text_format_table.format_table import FormatTable

PROG = "csv2table"
EXIT_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser.

    Defaults for -s and -w are None so they can be filled from the config.

    Returns:
        The configured parser.
    """
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Format a delimited file as a decimal aligned text or LaTeX table.",
    )
    parser.add_argument("files", nargs="*", help="Input files (default: stdin).")
    parser.add_argument(
        "-l", "--latex", action="store_true", help="Generate LaTeX table (uses siunitx)."
    )
    parser.add_argument(
        "-s",
        "--sig-figs",
        dest="sf",
        type=int,
        default=None,
        help=f"Significant figures (default is {DEFAULT_CONFIG.default_sig_figs}).",
    )
    parser.add_argument(
        "-c",
        "--sig-figs-by-column",
        dest="sflist",
        default=None,
        help='Significant figures by column as list e.g. "[1,2,2,2,4]"',
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        dest="delim",
        default=",",
        help="Input file delimiter (default is comma)",
    )
    parser.add_argument(
        "-w",
        "--max-column-width",
        dest="max_col_width",
        type=int,
        default=None,
        help="Maximum column width in characters "
        f"(default is {DEFAULT_CONFIG.max_column_width} char)",
    )
    parser.add_argument(
        "--config", default=None, help="TOML file overriding separators, defaults and paging."
    )
    return parser


def read_rows(paths: Sequence[str], delimiter: str) -> list[list[str]]:
    """Read delimited rows from paths, or stdin when paths is empty.

    Args:
        paths: Input file paths.
        delimiter: Field delimiter.

    Returns:
        The parsed rows.
    """
    with fileinput.input(files=list(paths)) as lines:
        return list(csv.reader(lines, delimiter=delimiter))


def build_table(args: argparse.Namespace, config: FormatConfig) -> FormatTable:
    """Create the FormatTable described by parsed arguments.

    Args:
        args: Parsed command line arguments.
        config: Active configuration.

    Returns:
        The formatted table.
    """
    sig_figs = args.sf
    if sig_figs is None and args.sflist is None:
        sig_figs = config.default_sig_figs
    max_col_width = config.max_column_width if args.max_col_width is None else args.max_col_width
    return FormatTable(
        read_rows(args.files, args.delim),
        sig_figs,
        args.latex,
        args.sflist,
        max_col_width,
        config=config,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line tool.

    Args:
        argv: Arguments excluding the program name (default: sys.argv[1:]).

    Returns:
        Process exit status (0 on success).
    """
    args = build_parser().parse_args(argv)
    try:
        config = DEFAULT_CONFIG if args.config is None else load_config(args.config)
        table = build_table(args, config)
    except (TextFormatTableError, OSError) as error:
        print(f"{PROG}: error: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(table)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
