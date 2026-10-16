"""Decimal aligned text and LaTeX tables with significant-figure control."""

from text_format_table.config import DEFAULT_CONFIG, FormatConfig, NumberFormat, load_config
from text_format_table.exceptions import (
    ColumnCountMismatchError,
    ColumnWidthError,
    ConfigError,
    EmptyTableError,
    InvalidSignificantFiguresError,
    TextFormatTableError,
)
from text_format_table.fnumber import FNumber
from text_format_table.format_table import (
    ColumnOffsets,
    FormatTable,
    OutputFormat,
    TableStyle,
    parse_sig_fig_list,
)

__author__ = "Scott Hendrickson"
__version__ = "2.0.0"
__email__ = "scott@drskippy.net"

__all__ = [
    "DEFAULT_CONFIG",
    "ColumnCountMismatchError",
    "ColumnOffsets",
    "ColumnWidthError",
    "ConfigError",
    "EmptyTableError",
    "FNumber",
    "FormatConfig",
    "FormatTable",
    "InvalidSignificantFiguresError",
    "NumberFormat",
    "OutputFormat",
    "TableStyle",
    "TextFormatTableError",
    "load_config",
    "parse_sig_fig_list",
]
