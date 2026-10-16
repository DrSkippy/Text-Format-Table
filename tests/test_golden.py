"""Characterization tests: output must stay byte-identical to the original tool.

The fixtures in tests/golden were produced by a line-for-line Python 3 port of
the original Python 2 code and match the README examples.
"""

import pytest
from conftest import GOLDEN_DIR

from text_format_table.cli import main
from text_format_table.demo import fnumber_demo, format_table_demo


def test_format_table_demo_matches_golden(capsys, golden):
    format_table_demo()
    assert capsys.readouterr().out == golden("format_table_demo.txt")


def test_fnumber_demo_matches_golden(capsys, golden):
    fnumber_demo()
    captured = capsys.readouterr()
    assert captured.out == golden("fnumber_demo.txt")
    assert "What does 0 significant figures mean?" in captured.err


@pytest.mark.parametrize(
    ("args", "fixture"),
    [
        (["-s", "4"], "test_csv_sf4.txt"),
        ([], "test_csv_sf4.txt"),  # default sf is 4
        (["-s", "3", "-l"], "test_csv_sf3_latex.txt"),
        (["-c", "[1,2,3,5]"], "test_csv_sflist.txt"),
        (["-s", "4", "-w", "6"], "test_csv_width6.txt"),
    ],
)
def test_cli_matches_golden(capsys, golden, test_csv, args, fixture):
    assert main([*args, test_csv]) == 0
    assert capsys.readouterr().out == golden(fixture)


def test_cli_page_break_matches_golden(capsys, golden):
    assert main([str(GOLDEN_DIR / "paged.csv")]) == 0
    out = capsys.readouterr().out
    assert out == golden("paged_sf4.txt")
    assert out.count("Header 1") == 2  # header repeated after 44 rows
