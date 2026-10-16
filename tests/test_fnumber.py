import math

import pytest

from text_format_table import (
    ColumnWidthError,
    FNumber,
    InvalidSignificantFiguresError,
    NumberFormat,
)
from text_format_table.fnumber import (
    digit_widths,
    format_number,
    group_digits,
    parse_number,
    round_half_up,
    round_to_sig_figs,
    truncate_text,
)

DEFAULT_FORMAT = NumberFormat()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.5", 1.5),
        (" 2 ", 2.0),
        (3, 3.0),
        ("-0.25", -0.25),
        ("abc", None),
        ("nan", None),
        ("inf", None),
        (math.inf, None),
        ("", None),
    ],
)
def test_parse_number(raw, expected):
    assert parse_number(raw) == expected


def test_parse_number_rejects_non_numeric_types():
    with pytest.raises(TypeError):
        parse_number(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "expected"), [(0.5, 1.0), (1.5, 2.0), (2.5, 3.0), (3.5, 4.0), (2.4999, 2.0)]
)
def test_round_half_up_rounds_ties_away_from_zero(value, expected):
    assert round_half_up(value) == expected


def test_round_to_sig_figs():
    assert round_to_sig_figs(1234.234, 2) == (1200.0, 3)
    assert round_to_sig_figs(-0.0023456, 2) == (0.0023, -3)
    assert round_to_sig_figs(0.0, 3) == (0.0, 0)


@pytest.mark.parametrize(
    ("decade", "sig_figs", "expected"),
    [(3, 2, (4, 0)), (3, 6, (4, 2)), (0, 3, (0, 2)), (-3, 2, (0, 4))],
)
def test_digit_widths(decade, sig_figs, expected):
    assert digit_widths(decade, sig_figs) == expected


@pytest.mark.parametrize(
    ("digits", "from_right", "expected"),
    [
        ("1234567", True, "1,234,567"),
        ("123", True, "123"),
        ("", True, ""),
        ("1234567", False, "123,456,7"),
        ("12", False, "12"),
        ("", False, ""),
    ],
)
def test_group_digits(digits, from_right, expected):
    assert group_digits(digits, ",", 3, from_right=from_right) == expected


@pytest.mark.parametrize(
    ("value", "sig_figs", "expected"),
    [
        (1234.234, 1, "1,000."),
        (1234.234, 9, "1,234.234 00"),
        (-1234.234, 5, "-1,234.2"),
        (0.000023456789, 5, "0.000 023 457"),
        (23456789.123345, 11, "23,456,789.123"),
        (0, 3, "0.00"),
        (9.99, 2, "10.0"),  # rounding crosses a decade
        (0.125, 2, "0.13"),  # exact binary tie rounds away from zero (Python 2)
        (2.5, 1, "3."),
    ],
)
def test_format_number(value, sig_figs, expected):
    assert format_number(value, sig_figs, DEFAULT_FORMAT) == expected


def test_format_number_latex_drops_thousands_separator():
    assert format_number(-1234567.5, 9, DEFAULT_FORMAT, latex=True) == "-1234567.50"


def test_format_number_custom_separators():
    european = NumberFormat(int_separator=".", decimal_separator=",", digit_group_size=3)
    assert format_number(1234.5678, 8, european) == "1.234,567 8"


@pytest.mark.parametrize(
    ("text", "width", "expected"),
    [
        ("Header 1", None, "Header 1"),
        ("Header 1", 8, "Header 1"),
        ("Header 1", 6, "Hea..."),
        ("Header 1", 3, "..."),
    ],
)
def test_truncate_text(text, width, expected):
    assert truncate_text(text, width, "...") == expected


def test_truncate_text_width_shorter_than_ellipsis():
    with pytest.raises(ColumnWidthError):
        truncate_text("Header 1", 2, "...")


def test_fnumber_numeric_attributes():
    number = FNumber("-1234.234", 5)
    assert number.is_numeric
    assert (number.sig_figs, number.value, number.sign) == (5, -1234.234, "-")
    assert number.sig_value == 1234.2
    assert number.value_str == "-1,234.2"
    assert number.size() == 8
    assert number.offset == 7
    assert number.right_offset == 1
    assert str(number) == "-1,234.2"
    assert "FNumber('-1234.234'" in repr(number)


def test_fnumber_text_attributes():
    number = FNumber("hello there", 0)
    assert not number.is_numeric
    assert (number.sig_figs, number.value, number.sign, number.sig_value) == (0, 0.0, "", 0.0)
    assert number.value_str == "hello there"
    assert number.offset == 1 + 11 // 2


def test_fnumber_text_latex_and_truncation():
    assert FNumber("column 1", 0, latex=True).value_str == "{column 1}"
    assert FNumber("a long header", 4, max_col_width=6).value_str == "a l..."
    assert FNumber("a long header", 4, True, 6).value_str == "{a l...}"


def test_fnumber_nan_and_inf_are_text():
    assert FNumber(math.nan, 3).value_str == "nan"
    assert FNumber("inf", 3).value_str == "inf"


@pytest.mark.parametrize("sig_figs", [0, -1])
def test_fnumber_rejects_non_positive_sig_figs_for_numbers(sig_figs):
    with pytest.raises(InvalidSignificantFiguresError, match="significant figures mean"):
        FNumber(1234.234, sig_figs)


def test_fnumber_pad():
    number = FNumber(123.234, 4)
    assert number.pad(12, 6) == "  123.2     "
    with pytest.raises(ColumnWidthError):
        number.pad(12, 2)
    with pytest.raises(ColumnWidthError):
        number.pad(3, 4)


def test_fnumber_deprecated_aliases():
    number = FNumber(123.234, 4)
    with pytest.deprecated_call():
        assert number.getOffset() == number.offset
    with pytest.deprecated_call():
        assert number.getRightOffset() == number.right_offset
    with pytest.deprecated_call():
        assert number.getPadded(10, 5) == number.pad(10, 5)
