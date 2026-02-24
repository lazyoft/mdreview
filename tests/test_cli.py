"""Tests for CLI entry point."""

from click.testing import CliRunner

from mdreview.cli import main


def test_version_flag_prints_version():
    """mdreview --version prints package name and version, exits 0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "mdreview" in result.output
    assert "version" in result.output


def test_version_flag_without_files():
    """--version works without providing any markdown files."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "mdreview" in result.output
