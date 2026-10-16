# Text-Format-Table

**Format CSV files as equally spaced text tables or LaTeX tables, and control
the significant figures displayed for a whole table, per column, or per value.**

This is a simple Python text formatting project. After searching for this
capability for a little while, I decided to write my own as the following
requirements seemed to be unique:

* Create a table of numbers from a CSV file
* Control the number of significant figures (significant digits) displayed
* Format numbers with "," and " " like this: `123,456.789 123`
* Align columns on decimal points; this is best for readability
* Fit the columns automatically based on data and formatting

There are many code snippets that do one part or another of this, but I didn't
find anything that fulfilled all the requirements, so I created a couple of
simple classes to accomplish the task. One caveat is that the output needs to
be displayed in a constant-width (monospace) font.

Text table output is the default. Use `-l` to create LaTeX output.

## Contents

- [Requirements and installation](#requirements-and-installation)
- [Command-line usage](#command-line-usage)
- [Examples](#examples)
- [How values are formatted](#how-values-are-formatted)
- [LaTeX output](#latex-output)
- [Python API](#python-api)
- [Configuration file](#configuration-file)
- [Development](#development)
- [Changes in 2.0](#changes-in-20)
- [License](#license)

## Requirements and installation

Python 3.11 or newer. There are no runtime dependencies.

```sh
pip install .            # installs the text_format_table package and the csv2table command
pip install -e ".[dev]"  # editable install with test and lint tools
```

You can also run the scripts straight from a checkout without installing:
`./csv2table.py`, `python3 FormatTable.py` and `python3 FNumber.py` all still work.

## Command-line usage

```sh
csv2table data.csv                  # 4 significant figures (the default)
cat data.csv | csv2table -s 3       # read stdin, 3 significant figures
csv2table -c "[2,3,4,2]" data.csv   # significant figures per column
csv2table -d ";" -w 20 data.csv     # semicolon delimited, text cut to 20 chars
csv2table -l -s 3 data.csv > t.tex  # LaTeX table
```

For example, using the first rows of the included `test.csv`:

```text
$ head -4 test.csv | csv2table -s 3
      Header 1 |   Header 2 |  Header 3 |  Header 4
------------------------------------------------------
  483,000.     |   472.     |    0.461  |    0.000 450
  966,000.     |   943.     |    0.921  |    0.000 900
1,450,000.     | 1,420.     |    1.38   |    0.001 35
```

Full help (`csv2table -h`, or `./csv2table.py -h`):

```text
usage: csv2table [-h] [-l] [-s SF] [-c SFLIST] [-d DELIM] [-w MAX_COL_WIDTH]
                 [--config CONFIG]
                 [files ...]

Format a delimited file as a decimal aligned text or LaTeX table.

positional arguments:
  files                 Input files (default: stdin).

options:
  -h, --help            show this help message and exit
  -l, --latex           Generate LaTeX table (uses siunitx).
  -s, --sig-figs SF     Significant figures (default is 4).
  -c, --sig-figs-by-column SFLIST
                        Significant figures by column as list e.g.
                        "[1,2,2,2,4]"
  -d, --delimiter DELIM
                        Input file delimiter (default is comma)
  -w, --max-column-width MAX_COL_WIDTH
                        Maximum column width in characters (default is 50
                        char)
  --config CONFIG       TOML file overriding separators, defaults and paging.
```

How the command behaves:

- **Header row.** The first row is treated as the header. A rule is drawn
  under it, and the header is repeated every 44 rows (counting the header
  itself). You can change that with `rows_per_page` in a
  [configuration file](#configuration-file).
- **Several input files** are read one after another into a single table, so
  only the first row of the first file is the header.
- **Significant figures:** `-s` wins over `-c`. With neither, the default of 4
  is used (or `default_sig_figs` from the configuration file).
- **`-c` list:** a comma-separated list of integers, with or without
  brackets, e.g. `"[1,2,2,4]"`, `"1,2,2,4"` or `"(1,2,2,4)"`. Rows shorter than
  the list are fine. A row longer than the list is an error rather than
  having its extra columns dropped.
- **`-w`** only shortens text cells; numbers are never cut. Longer text is
  shortened to the width with `...` at the end. The default is 50.
- **Exit status** is 0 on success. It is 2 for invalid input (bad `-c` list,
  column-count mismatch, 0 significant figures for a number, unreadable file,
  invalid configuration), with a `csv2table: error: ...` message on stderr.

## Examples

These tables are produced by `python -m text_format_table.demo`.

Custom significant figures per value:

```text
      column 1       |        column 2         |       column C    |    another column
-----------------------------------------------------------------------------------------
     1,000.          |       1,200.            |      1,230.       |        123.
       123.2         |       1,000.            |        123.2      |      1,234.
     1,234.2         |      -1,234.2           |      1,234.23     |      1,234.234
     1,234.234 00    |           0.2           |          0.23     |         -0.23
         0.235       |           0.234 6       |          0.234 57 |          0.002 35
         0.000 234 6 |           0.000 023 457 | 23,000,000.       | 23,460,000.
23,456,800.          | -23,456,800.            | 23,456,789.       | 23,456,789.123 345 0
-----------------------------------------------------------------------------------------
```

The same values with a constant 3 significant figures (`csv2table -s 3` does
this for a CSV file):

```text
      column 1     |        column 2       |       column C |    another column
-------------------------------------------------------------------------------
     1,230.        |       1,230.          |      1,230.    |        123.
       123.        |       1,230.          |        123.    |      1,230.
     1,230.        |      -1,230.          |      1,230.    |      1,230.
     1,230.        |           0.235       |          0.235 |         -0.235
         0.235     |           0.235       |          0.235 |          0.002 35
         0.000 235 |           0.000 023 5 | 23,500,000.    | 23,500,000.
23,500,000.        | -23,500,000.          | 23,500,000.    | 23,500,000.
-------------------------------------------------------------------------------
```

The same table as LaTeX (`-l`), which needs the `siunitx` package:

```latex
%% Table generated by formatTable utility %%
%% add \usepackage[group-separator={,}]{siunitx}
%%
\begin{table}
\begin{tabular}{|S|S|S|S|}
\hline
   {column 1}    &     {column 2}      &    {column C} & {another column} \\
\hline
    1230.        &      1230.          &     1230.     &      123.        \\
     123.        &      1230.          &      123.     &     1230.        \\
    1230.        &     -1230.          &     1230.     &     1230.        \\
    1230.        &         0.235       &        0.235  &       -0.235     \\
       0.235     &         0.235       &        0.235  &        0.002 35  \\
       0.000 235 &         0.000 023 5 & 23500000.     & 23500000.        \\
23500000.        & -23500000.          & 23500000.     & 23500000.        \\
\hline
\end{tabular}
\end{table}
%% Table generated by formatTable utility %%
```

## How values are formatted

- **Numbers** are rounded to the requested significant figures. Exact ties
  round away from zero, the same as 1.x (Python 2), so `0.125` at 2
  significant figures is `0.13`.
- **The decimal point is always shown**, and digits to the left of the
  significant ones are filled with zeros: `1234.234` at 1 significant figure
  is `1,000.` and at 9 it is `1,234.234 00`, with trailing zeros kept.
- **Digit grouping:** thousands are separated with `,` and thousandths with a
  space (`23,456,789.123 345 0`). The separators, group size and decimal
  point can be changed in the [configuration file](#configuration-file).
- **Alignment:** numbers in a column line up on their decimal points, and the
  column width fits the widest value.
- **Text** is anything that does not parse as a finite number, including
  `nan` and `inf`. It is centred on the column's decimal position and is not
  rounded. Text cells may have 0 significant figures. A number with 0 or
  fewer significant figures is an error.

## LaTeX output

`-l` (or `latex=True`) produces a `tabular` with one siunitx `S` column per
column. Add `\usepackage[group-separator={,}]{siunitx}` to your preamble.
In LaTeX mode, thousands separators are left out (siunitx inserts its own),
thousandths spacing is kept, and text cells are wrapped in `{...}` so siunitx
treats them as text. Each page of rows becomes its own `table` environment.

Note: LaTeX special characters in text cells (`& % $ # _ { } ~ ^ \`) are not
escaped. Escape them in your data if they appear.

## Python API

```python
from text_format_table import FormatTable

# One significant-figure value for every cell
print(FormatTable([["name", "value"], ["a", "1234.5"], ["b", "0.0123"]], sf=3))
```

```text
name |    value
------------------
  a  | 1,230.
  b  |     0.012 3
```

Significant figures can be set three ways (`sf` wins over `sflist`):

```python
FormatTable(rows, sf=3)                  # whole table
FormatTable(rows, sflist=[2, 3, 4])      # per column (a list, or a string like "[2,3,4]")
FormatTable([[("item", 0), ("mass", 0)], # per value: each cell is (value, sig_figs)
             [("apple", 0), (0.15234, 2)],
             [("truck", 0), (3500.7, 5)]])
```

`FormatTable(table, sf=None, latex=False, sflist=None, max_col_width=None, config=DEFAULT_CONFIG)`

- `render()` (or `str(table)`) returns the table text.
- Attributes: `cells` (rows of `FNumber`), `offsets` (`ColumnOffsets`),
  `style` (`TableStyle`), `output_format` (`OutputFormat.TEXT` or `.LATEX`).
- In the library `max_col_width` defaults to `None` (no limit). The 50
  character default applies only to the command line.

`FNumber(raw, sig_figs, latex=False, max_col_width=None, number_format=...)`
formats a single value:

```python
from text_format_table import FNumber

n = FNumber(1234.567, 5)
n.value_str          # '1,234.6'
n.offset             # 6  (characters up to and including the decimal point)
n.right_offset       # 1
n.pad(12, 6)         # '1,234.6     '
```

Lower-level helpers in `text_format_table.fnumber`: `parse_number`,
`round_half_up`, `round_to_sig_figs`, `digit_widths`, `group_digits`,
`format_number` and `truncate_text`. `parse_sig_fig_list` is in
`text_format_table.format_table`.

**Exceptions.** All of these derive from `TextFormatTableError`, and from
`ValueError`, so existing `except ValueError` handlers still catch them.

| Exception | Raised when |
|---|---|
| `InvalidSignificantFiguresError` | a number gets 0 or fewer significant figures, or an `sf` / `sflist` value is not an integer |
| `ColumnCountMismatchError` | a row has more columns than `sflist` |
| `ColumnWidthError` | a value does not fit its column, or `max_col_width` is shorter than the ellipsis |
| `EmptyTableError` | the table has no rows |
| `ConfigError` | a configuration file or value is invalid |

**Backwards compatibility.** `from FNumber import FNumber` and
`from FormatTable import FormatTable` still work from a checkout. The old
`getOffset()`, `getRightOffset()` and `getPadded()` methods still work but give
a `DeprecationWarning`; use `offset`, `right_offset` and `pad()` instead.

## Configuration file

Everything that used to be hard-coded can be changed in a TOML file, passed with
`--config` on the command line or loaded with `load_config()` in Python.
Command-line flags win over the file. These are the defaults; any key can be
left out:

```toml
default_sig_figs = 4    # used when neither -s nor -c is given
max_column_width = 50   # default for -w
rows_per_page = 44      # repeat the header after this many rows

[number]
int_separator = ","        # thousands
mantissa_separator = " "   # thousandths
decimal_separator = "."
digit_group_size = 3
ellipsis = "..."           # suffix for shortened text
```

```python
from text_format_table import FormatConfig, FormatTable, NumberFormat, load_config

config = load_config("table.toml")
# or build one in code, e.g. European style: 1.234.567,9
european = FormatConfig(number=NumberFormat(int_separator=".", decimal_separator=","))
print(FormatTable(rows, sf=4, config=european))
```

The file is checked when loaded. Unknown keys, values that aren't positive
integers, an empty decimal separator, a decimal separator that matches a
grouping separator, or a `max_column_width` shorter than the ellipsis all
raise `ConfigError`.

## Development

```sh
pip install -e ".[dev]"
pytest                    # tests with coverage; fails below 85%
ruff check . && ruff format --check .
mypy                      # strict mode
```

`tests/golden/` holds reference output from the original 1.x code. The
golden tests check that the output stays byte-for-byte identical. GitHub
Actions runs lint, type checks and tests on Python 3.11 to 3.13.

```text
text_format_table/
  fnumber.py        FNumber and number formatting helpers
  format_table.py   FormatTable, TableStyle, ColumnOffsets, OutputFormat
  config.py         FormatConfig, NumberFormat, load_config
  exceptions.py     exception classes
  cli.py            csv2table command
  demo.py           the examples above
FNumber.py, FormatTable.py, csv2table.py   compatibility entry points
tests/              pytest suite and golden output
```

## Changes in 2.0

- Ported to Python 3. Output is byte-identical to 1.x; ties still round away
  from zero, as Python 2 did.
- The code is now the `text_format_table` package with a `csv2table` command.
  `FNumber.py`, `FormatTable.py` and `csv2table.py` remain as compatibility
  entry points.
- `-c` no longer runs its argument as Python code; it takes a list of
  integers such as `"[1,2,2,4]"` or `"1,2,2,4"`.
- `-w` now works when given on the command line; before, it was ignored.
- New `--config` TOML file for separators, defaults and rows per page.
- Problems raise exceptions (and the command exits with status 2) instead of
  exiting with status 0 or printing a warning and producing misaligned output.
  This covers 0 or fewer significant figures for a number, a row with more
  columns than the `-c` list (those columns used to be silently dropped), an
  empty table, and a max column width shorter than the ellipsis.
- The camelCase methods `getOffset` / `getRightOffset` / `getPadded` are
  deprecated in favour of `offset` / `right_offset` / `pad()`. Keyword
  arguments are snake_case (`maxColWidth` is now `max_col_width`); positional
  calls are unchanged.
- Licensed under LGPL-3.0-or-later (1.x was CC BY-SA 3.0 US).

Enjoy!

## License

Copyright (C) 2011-2026 Scott Hendrickson

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version (SPDX: `LGPL-3.0-or-later`).

This library is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You can use the library from any program, including proprietary ones. Modified
versions of the library itself must be shared under the same license. See
[COPYING.LESSER](COPYING.LESSER) and [COPYING](COPYING) for the full terms.

Versions 1.x were released under
[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/).
