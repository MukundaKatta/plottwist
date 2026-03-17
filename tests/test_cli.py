"""Tests for the CLI commands (non-interactive)."""

from click.testing import CliRunner

from plottwist.cli import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "plottwist" in result.output


def test_templates_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["templates"])
    assert result.exit_code == 0
    assert "mystery" in result.output.lower()
    assert "fantasy" in result.output.lower()
    assert "scifi" in result.output.lower()


def test_play_requires_template_or_save():
    runner = CliRunner()
    result = runner.invoke(cli, ["play"])
    assert result.exit_code != 0
