import pytest

from text_format_table import ConfigError, FormatConfig, NumberFormat, load_config
from text_format_table.config import config_from_dict


def test_defaults_match_original_constants():
    config = FormatConfig()
    assert (config.default_sig_figs, config.max_column_width, config.rows_per_page) == (4, 50, 44)
    assert config.number == NumberFormat(",", " ", ".", 3, "...")


def test_load_config(tmp_path):
    path = tmp_path / "table.toml"
    path.write_text('rows_per_page = 10\ndefault_sig_figs = 3\n[number]\nint_separator = "_"\n')
    config = load_config(path)
    assert config.rows_per_page == 10
    assert config.default_sig_figs == 3
    assert config.max_column_width == 50
    assert config.number.int_separator == "_"


def test_load_config_invalid_toml(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_text("rows_per_page = = 3")
    with pytest.raises(ConfigError):
        load_config(path)


@pytest.mark.parametrize(
    "data",
    [
        {"rows_per_pages": 3},
        {"number": {"thousands": ","}},
        {"number": "x"},
        {"rows_per_page": 0},
        {"rows_per_page": True},
        {"default_sig_figs": "4"},
        {"max_column_width": 2},
        {"number": {"decimal_separator": ""}},
        {"number": {"decimal_separator": ","}},
        {"number": {"int_separator": 1}},
        {"number": {"digit_group_size": 0}},
    ],
)
def test_invalid_config_values(data):
    with pytest.raises(ConfigError):
        config_from_dict(data)


def test_number_must_be_number_format():
    with pytest.raises(ConfigError):
        FormatConfig(number={"int_separator": ","})  # type: ignore[arg-type]
