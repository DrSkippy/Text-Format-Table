import io
import subprocess
import sys

from conftest import REPO_ROOT

from text_format_table.cli import build_parser, main


def test_reads_stdin_with_custom_delimiter(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a;b\n1234.5;0.5\n"))
    assert main(["-d", ";", "-s", "2"]) == 0
    out = capsys.readouterr().out
    assert "1,200." in out and "0.50" in out


def test_config_file_overrides_defaults(tmp_path, capsys, test_csv):
    config = tmp_path / "c.toml"
    config.write_text("default_sig_figs = 2\nmax_column_width = 5\n")
    assert main(["--config", str(config), test_csv]) == 0
    out = capsys.readouterr().out
    assert " H..." in out and "480,000." in out


def test_flags_override_config(tmp_path, capsys, test_csv):
    config = tmp_path / "c.toml"
    config.write_text("default_sig_figs = 2\n")
    assert main(["--config", str(config), "-s", "4", test_csv]) == 0
    assert "483,000." in capsys.readouterr().out


def test_bad_sig_fig_list_reports_error(capsys, test_csv):
    assert main(["-c", "__import__('os').system('true')", test_csv]) == 2
    assert "csv2table: error:" in capsys.readouterr().err


def test_short_sig_fig_list_reports_error(capsys, test_csv):
    assert main(["-c", "[1,2]", test_csv]) == 2
    assert "only 2 significant figure values" in capsys.readouterr().err


def test_missing_file_reports_error(capsys, tmp_path):
    assert main([str(tmp_path / "missing.csv")]) == 2
    assert "csv2table: error:" in capsys.readouterr().err


def test_bad_config_reports_error(capsys, tmp_path, test_csv):
    config = tmp_path / "c.toml"
    config.write_text("rows_per_page = -1\n")
    assert main(["--config", str(config), test_csv]) == 2


def test_parser_converts_numeric_options():
    args = build_parser().parse_args(["-s", "3", "-w", "20"])
    assert (args.sf, args.max_col_width) == (3, 20)


def test_legacy_script_runs(test_csv, golden):
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "csv2table.py"), "-s3", "-l", test_csv],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    assert result.stdout == golden("test_csv_sf3_latex.txt")


def test_legacy_imports():
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from FNumber import FNumber as LegacyFNumber
        from FormatTable import FormatTable as LegacyFormatTable
        from text_format_table import FNumber, FormatTable

        assert LegacyFNumber is FNumber
        assert LegacyFormatTable is FormatTable
    finally:
        sys.path.remove(str(REPO_ROOT))
