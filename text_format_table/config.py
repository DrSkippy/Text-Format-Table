# SPDX-License-Identifier: LGPL-3.0-or-later
"""Formatting configuration: separators, defaults and paging.

Every tunable factor lives here instead of being hard coded in the formatting
logic. Values can be overridden from a TOML file (see ``load_config``)::

    default_sig_figs = 4
    max_column_width = 50
    rows_per_page = 44

    [number]
    int_separator = ","
    mantissa_separator = " "
    decimal_separator = "."
    digit_group_size = 3
    ellipsis = "..."
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

from text_format_table.exceptions import ConfigError


def _require_positive_int(name: str, value: object) -> None:
    """Raise ConfigError unless value is a positive int (bools rejected).

    Args:
        name: Setting name used in the error message.
        value: Value to check.

    Raises:
        ConfigError: If value is not a positive int.
    """
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{name} must be a positive integer, got {value!r}")


def _require_str(name: str, value: object) -> None:
    """Raise ConfigError unless value is a str.

    Args:
        name: Setting name used in the error message.
        value: Value to check.

    Raises:
        ConfigError: If value is not a str.
    """
    if not isinstance(value, str):
        raise ConfigError(f"{name} must be a string, got {value!r}")


@dataclass(frozen=True)
class NumberFormat:
    """Separators used when rendering a number.

    Attributes:
        int_separator: Separator for thousands, e.g. ``123,456``.
        mantissa_separator: Separator for thousandths, e.g. ``0.123 456``.
        decimal_separator: Decimal point written to the output.
        digit_group_size: Number of digits between separators.
        ellipsis: Suffix appended to text truncated to the max column width.
    """

    # customize separators if necessary
    int_separator: str = ","
    mantissa_separator: str = " "
    decimal_separator: str = "."
    digit_group_size: int = 3
    ellipsis: str = "..."

    def __post_init__(self) -> None:
        """Validate the separators.

        Raises:
            ConfigError: If a value has the wrong type or the decimal separator
                is empty or collides with another separator.
        """
        for name in ("int_separator", "mantissa_separator", "decimal_separator", "ellipsis"):
            _require_str(name, getattr(self, name))
        _require_positive_int("digit_group_size", self.digit_group_size)
        if not self.decimal_separator:
            raise ConfigError("decimal_separator must not be empty")
        if self.decimal_separator in (self.int_separator, self.mantissa_separator):
            raise ConfigError("decimal_separator must differ from the digit group separators")


@dataclass(frozen=True)
class FormatConfig:
    """Top-level formatting configuration.

    Attributes:
        default_sig_figs: Significant figures used by the CLI when neither
            ``--sig-figs`` nor ``--sig-figs-by-column`` is given.
        max_column_width: Default maximum width of text cells in the CLI.
        rows_per_page: Rows after which the table footer, header and header
            row are repeated.
        number: Number separator settings.
    """

    default_sig_figs: int = 4
    max_column_width: int = 50
    rows_per_page: int = 44
    number: NumberFormat = field(default_factory=NumberFormat)

    def __post_init__(self) -> None:
        """Validate the numeric settings.

        Raises:
            ConfigError: If a setting is not a positive int or the max column
                width cannot hold the ellipsis.
        """
        for name in ("default_sig_figs", "max_column_width", "rows_per_page"):
            _require_positive_int(name, getattr(self, name))
        if not isinstance(self.number, NumberFormat):
            raise ConfigError(f"number must be a NumberFormat, got {self.number!r}")
        if self.max_column_width < len(self.number.ellipsis):
            raise ConfigError("max_column_width must be at least as long as the ellipsis")


def _known_keys(cls: type) -> set[str]:
    """Return the dataclass field names of cls."""
    return {f.name for f in fields(cls)}


def _check_keys(section: str, data: dict[str, Any], allowed: set[str]) -> None:
    """Raise ConfigError if data contains keys outside allowed.

    Args:
        section: Section name used in the error message.
        data: Parsed TOML table.
        allowed: Permitted keys.

    Raises:
        ConfigError: If unknown keys are present.
    """
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ConfigError(f"unknown {section} setting(s): {', '.join(unknown)}")


def config_from_dict(data: dict[str, Any]) -> FormatConfig:
    """Build a FormatConfig from a parsed TOML mapping.

    Missing keys keep their defaults.

    Args:
        data: Mapping with top-level settings and an optional ``number`` table.

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If keys are unknown or values are invalid.
    """
    top_level = dict(data)
    number_data = top_level.pop("number", {})
    if not isinstance(number_data, dict):
        raise ConfigError("[number] must be a table")
    _check_keys("top-level", top_level, _known_keys(FormatConfig) - {"number"})
    _check_keys("[number]", number_data, _known_keys(NumberFormat))
    return FormatConfig(number=NumberFormat(**number_data), **top_level)


def load_config(path: str | Path) -> FormatConfig:
    """Load a FormatConfig from a TOML file.

    Args:
        path: Path to the TOML file.

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If the file is not valid TOML or contains invalid settings.
        OSError: If the file cannot be read.
    """
    with open(path, "rb") as config_file:
        try:
            data = tomllib.load(config_file)
        except tomllib.TOMLDecodeError as error:
            raise ConfigError(f"{path}: {error}") from error
    return config_from_dict(data)


DEFAULT_CONFIG = FormatConfig()
