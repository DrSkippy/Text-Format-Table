"""Significant-figure number formatting with thousands/thousandths separators."""

from __future__ import annotations

import math
import warnings
from decimal import ROUND_HALF_UP, Decimal

from text_format_table.config import DEFAULT_CONFIG, NumberFormat
from text_format_table.exceptions import ColumnWidthError, InvalidSignificantFiguresError

# Decimal point emitted by Python's own %-formatting, independent of config.
_PY_DECIMAL_POINT = "."

Cell = str | float


def parse_number(raw: Cell) -> float | None:
    """Parse raw as a finite float.

    Args:
        raw: A number or a string that may hold one.

    Returns:
        The float value, or None if raw is text, NaN or infinite (such values
        are rendered as text).
    """
    try:
        value = float(raw)
    except ValueError:
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def round_half_up(value: float) -> float:
    """Round to the nearest integer, ties away from zero.

    Reproduces Python 2 ``round(x, 0)``; Python 3 ``round`` rounds ties to even,
    which would change significant-figure results on exact .5 boundaries.

    Args:
        value: Value to round. ``Decimal(value)`` is exact, so the tie test is
            done on the true binary value just like Python 2.

    Returns:
        The rounded value as a float.
    """
    return float(Decimal(value).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def round_to_sig_figs(value: float, sig_figs: int) -> tuple[float, int]:
    """Round abs(value) to sig_figs significant figures.

    Args:
        value: Finite value to round.
        sig_figs: Positive number of significant figures.

    Returns:
        Tuple of (rounded absolute value, decade of the original value), where
        decade is floor(log10(abs(value))) and 0 for zero.
    """
    if value == 0:
        return 0.0, 0
    decade = int(math.floor(math.log10(abs(value))))
    decade_factor = math.pow(10.0, sig_figs - decade - 1)
    return round_half_up(abs(value) * decade_factor) / decade_factor, decade


def digit_widths(decade: int, sig_figs: int) -> tuple[int, int]:
    """Compute the integer and mantissa widths for a rounded value.

    Args:
        decade: floor(log10(abs(value))), 0 for zero.
        sig_figs: Positive number of significant figures.

    Returns:
        Tuple of (integer width, mantissa width) passed to %-formatting.
    """
    # are any of the digits in int portion significant?
    int_size = decade + 1 if decade > 0 else 0
    if int_size > 0:  # at least one sig digit left of decimal
        mantissa_size = max(sig_figs - int_size, 0)
    else:  # int_size == 0
        mantissa_size = sig_figs - decade - 1
    return int_size, mantissa_size


def group_digits(digits: str, separator: str, group_size: int, *, from_right: bool) -> str:
    """Insert separator between groups of digits.

    Args:
        digits: Digit string to group.
        separator: Text inserted between groups.
        group_size: Digits per group.
        from_right: Group from the right (integer part, ``1,234``) instead of
            from the left (mantissa, ``.123 4``).

    Returns:
        The grouped digit string.
    """
    if from_right:
        head = len(digits) % group_size or group_size
        chunks = [digits[:head]]
        chunks += [digits[i : i + group_size] for i in range(head, len(digits), group_size)]
    else:
        chunks = [digits[i : i + group_size] for i in range(0, len(digits), group_size)]
    return separator.join(chunks)


def format_number(
    value: float, sig_figs: int, number_format: NumberFormat, latex: bool = False
) -> str:
    """Format value with sig_figs significant figures and digit grouping.

    Args:
        value: Finite value to format.
        sig_figs: Positive number of significant figures.
        number_format: Separator settings.
        latex: Omit thousands separators (siunitx adds its own).

    Returns:
        The formatted number, always containing the decimal separator.
    """
    # calculate the value to desire sig figs
    rounded, decade = round_to_sig_figs(value, sig_figs)
    int_size, mantissa_size = digit_widths(decade, sig_figs)
    fixed = f"{rounded:{int_size}.{mantissa_size}F}"
    int_digits, _, mantissa_digits = fixed.partition(_PY_DECIMAL_POINT)
    sign = "-" if value < 0 else ""
    int_separator = "" if latex else number_format.int_separator
    group_size = number_format.digit_group_size
    return (
        sign
        + group_digits(int_digits, int_separator, group_size, from_right=True)
        + number_format.decimal_separator
        + group_digits(
            mantissa_digits, number_format.mantissa_separator, group_size, from_right=False
        )
    )


def truncate_text(text: str, max_width: int | None, ellipsis: str) -> str:
    """Shorten text to max_width characters, ending in ellipsis.

    Args:
        text: Text to shorten.
        max_width: Maximum length, or None for no limit.
        ellipsis: Suffix marking truncated text.

    Returns:
        text unchanged if it fits, otherwise the truncated text.

    Raises:
        ColumnWidthError: If max_width is shorter than the ellipsis.
    """
    if max_width is None or len(text) <= max_width:
        return text
    if max_width < len(ellipsis):
        raise ColumnWidthError(
            f"max column width {max_width} is shorter than the ellipsis {ellipsis!r}"
        )
    return text[: max_width - len(ellipsis)] + ellipsis


class FNumber:
    """Significant-figure number (or text) cell.

    Float number container produces string formatted number representation with
    specified number of significant figures, "," separators for thousands and " "
    separators for thousanths.  Provides access to string size and offset to
    decimal.

    Text that does not parse as a finite number is kept as text.

    Attributes:
        raw: The original value.
        is_numeric: True if raw parsed as a finite number.
        sig_figs: Significant figures used (0 for text).
        value: Parsed value (0.0 for text).
        sign: "-" for negative numbers, else "".
        sig_value: Absolute value rounded to sig_figs (0.0 for text).
        value_str: Rendered representation.
    """

    def __init__(
        self,
        raw: Cell,
        sig_figs: int,
        latex: bool = False,
        max_col_width: int | None = None,
        number_format: NumberFormat = DEFAULT_CONFIG.number,
    ) -> None:
        """Parse and format raw.

        Args:
            raw: Number or string to format.
            sig_figs: Significant figures; must be positive when raw is numeric.
            latex: Produce siunitx-friendly output (text wrapped in braces, no
                thousands separators).
            max_col_width: Maximum width of text values, None for no limit.
            number_format: Separator settings.

        Raises:
            InvalidSignificantFiguresError: If raw is numeric and sig_figs <= 0.
            ColumnWidthError: If text must be truncated to fewer characters
                than the ellipsis.
        """
        self.raw = raw
        self.number_format = number_format
        parsed = parse_number(raw)
        self.is_numeric = parsed is not None
        if parsed is None:
            self._init_text(str(raw), latex, max_col_width)
        else:
            self._init_number(parsed, sig_figs, latex)

    def _init_text(self, text: str, latex: bool, max_col_width: int | None) -> None:
        """Store a text value.

        Args:
            text: The text to render.
            latex: Wrap the text in braces for siunitx.
            max_col_width: Maximum width of the text, None for no limit.
        """
        # string
        self.sig_figs = 0
        self.value = 0.0
        self.sign = ""
        self.sig_value = 0.0
        # max column width only applies to text fields
        text = truncate_text(text, max_col_width, self.number_format.ellipsis)
        self.value_str = "{" + text + "}" if latex else text

    def _init_number(self, value: float, sig_figs: int, latex: bool) -> None:
        """Store and format a numeric value.

        Args:
            value: Finite value.
            sig_figs: Significant figures.
            latex: Omit thousands separators.

        Raises:
            InvalidSignificantFiguresError: If sig_figs <= 0.
        """
        if sig_figs <= 0:
            raise InvalidSignificantFiguresError(
                f"What does {sig_figs} significant figures mean? (value {self.raw!r})"
            )
        # store the values
        self.sig_figs = int(sig_figs)
        self.value = value
        # set the sign
        self.sign = "-" if value < 0 else ""
        self.sig_value, _ = round_to_sig_figs(value, self.sig_figs)
        self.value_str = format_number(value, self.sig_figs, self.number_format, latex)

    def size(self) -> int:
        """Return the rendered width in characters."""
        return len(self.value_str)

    @property
    def offset(self) -> int:
        """Characters up to and including the decimal point (text: the center)."""
        # count, not index
        if self.is_numeric:
            return 1 + self.value_str.index(self.number_format.decimal_separator)
        return 1 + self.size() // 2

    @property
    def right_offset(self) -> int:
        """Characters to the right of the alignment offset."""
        return self.size() - self.offset

    def pad(self, width: int, offset: int) -> str:
        """Pad value_str to width so its alignment point lands at offset.

        Args:
            width: Total column width.
            offset: Column alignment offset (count, not index).

        Returns:
            The padded string, exactly width characters long.

        Raises:
            ColumnWidthError: If the value does not fit width at offset.
        """
        left = offset - self.offset
        right = width - left - self.size()
        if left < 0 or right < 0:
            raise ColumnWidthError(
                f"{self.value_str!r} does not fit column width {width} at offset {offset}"
            )
        return " " * left + self.value_str + " " * right

    def __str__(self) -> str:
        """Return the rendered value."""
        return self.value_str

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"FNumber({self.raw!r}, sig_figs={self.sig_figs}, value_str={self.value_str!r})"

    # Deprecated camelCase API kept for backwards compatibility.
    def getOffset(self) -> int:  # noqa: N802
        """Deprecated alias for :attr:`offset`."""
        warnings.warn("getOffset() is deprecated; use .offset", DeprecationWarning, stacklevel=2)
        return self.offset

    def getRightOffset(self) -> int:  # noqa: N802
        """Deprecated alias for :attr:`right_offset`."""
        warnings.warn(
            "getRightOffset() is deprecated; use .right_offset", DeprecationWarning, stacklevel=2
        )
        return self.right_offset

    def getPadded(self, width: int, offset: int) -> str:  # noqa: N802
        """Deprecated alias for :meth:`pad`."""
        warnings.warn("getPadded() is deprecated; use .pad()", DeprecationWarning, stacklevel=2)
        return self.pad(width, offset)
