"""Tests for CLI entry point."""

from importlib.metadata import version
from unittest.mock import patch

from click.testing import CliRunner

from mdreview.cli import detect_install_method, main


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


class TestDetectInstallMethod:
    def test_pipx(self):
        with patch("mdreview.cli.sys") as mock_sys:
            mock_sys.executable = "/home/user/.local/pipx/venvs/mdreview/bin/python"
            assert detect_install_method() == "pipx"

    def test_uv_tool(self):
        with patch("mdreview.cli.sys") as mock_sys:
            mock_sys.executable = "/home/user/.local/share/uv/tools/mdreview/bin/python"
            assert detect_install_method() == "uv"

    def test_pip_fallback(self):
        with patch("mdreview.cli.sys") as mock_sys:
            mock_sys.executable = "/usr/bin/python3"
            assert detect_install_method() == "pip"


class TestUpdateFlag:
    def test_update_new_version(self):
        runner = CliRunner()
        with (
            patch("mdreview.cli.run_upgrade", return_value=0),
            patch("mdreview.cli.get_installed_version", return_value="2.0.0"),
        ):
            result = runner.invoke(main, ["--update"])
        assert result.exit_code == 0
        assert "upgrading via" in result.output
        assert "Updated:" in result.output
        assert "2.0.0" in result.output

    def test_update_already_up_to_date(self):
        runner = CliRunner()
        current = version("mdreview")
        with (
            patch("mdreview.cli.run_upgrade", return_value=0),
            patch("mdreview.cli.get_installed_version", return_value=current),
        ):
            result = runner.invoke(main, ["--update"])
        assert result.exit_code == 0
        assert "Already up to date" in result.output

    def test_update_failure(self):
        runner = CliRunner()
        with patch("mdreview.cli.run_upgrade", return_value=1):
            result = runner.invoke(main, ["--update"])
        assert result.exit_code == 1
