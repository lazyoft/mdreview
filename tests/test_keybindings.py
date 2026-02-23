"""Tests for keybinding configuration loading and utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdreview.keybindings import (
    DEFAULT_BINDINGS,
    ensure_config,
    key_label,
    load_keybindings,
)


class TestLoadKeybindings:
    """Tests for load_keybindings."""

    def test_returns_defaults_when_no_file(self, tmp_path: Path) -> None:
        result = load_keybindings(tmp_path / "nonexistent.toml")
        assert result == DEFAULT_BINDINGS

    def test_returns_defaults_when_path_is_none_and_no_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "mdreview.keybindings.get_config_path",
            lambda: tmp_path / "nope" / "keys.toml",
        )
        result = load_keybindings(None)
        assert result == DEFAULT_BINDINGS

    def test_partial_override(self, tmp_path: Path) -> None:
        config = tmp_path / "keys.toml"
        config.write_text('[keys]\nquit = "x"\napprove = "a"\n')
        result = load_keybindings(config)
        assert result["quit"] == "x"
        assert result["approve"] == "a"
        # Others unchanged
        assert result["comment"] == DEFAULT_BINDINGS["comment"]

    def test_unknown_action_ignored(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        config = tmp_path / "keys.toml"
        config.write_text('[keys]\nfake_action = "z"\n')
        result = load_keybindings(config)
        assert result == DEFAULT_BINDINGS
        assert "unknown action 'fake_action'" in capsys.readouterr().err

    def test_invalid_toml(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        config = tmp_path / "keys.toml"
        config.write_text("this is not valid toml {{{}}")
        result = load_keybindings(config)
        assert result == DEFAULT_BINDINGS
        assert "failed to parse" in capsys.readouterr().err

    def test_non_string_value_ignored(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        config = tmp_path / "keys.toml"
        config.write_text("[keys]\nquit = 42\n")
        result = load_keybindings(config)
        assert result["quit"] == DEFAULT_BINDINGS["quit"]
        assert "not a string" in capsys.readouterr().err

    def test_keys_section_not_a_table(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        config = tmp_path / "keys.toml"
        config.write_text('keys = "not a table"\n')
        result = load_keybindings(config)
        assert result == DEFAULT_BINDINGS
        assert "not a table" in capsys.readouterr().err


class TestEnsureConfig:
    """Tests for ensure_config."""

    def test_creates_file_with_defaults(self, tmp_path: Path) -> None:
        config = tmp_path / "config" / "keys.toml"
        result = ensure_config(config)
        assert result == config
        assert config.exists()
        content = config.read_text()
        assert "[keys]" in content
        for action in DEFAULT_BINDINGS:
            assert action in content

    def test_preserves_existing_file(self, tmp_path: Path) -> None:
        config = tmp_path / "keys.toml"
        config.write_text("# my custom config\n")
        ensure_config(config)
        assert config.read_text() == "# my custom config\n"

    def test_created_config_is_loadable(self, tmp_path: Path) -> None:
        config = tmp_path / "keys.toml"
        ensure_config(config)
        result = load_keybindings(config)
        assert result == DEFAULT_BINDINGS


class TestKeyLabel:
    """Tests for key_label."""

    def test_question_mark(self) -> None:
        assert key_label("question_mark") == "?"

    def test_shift_up(self) -> None:
        assert key_label("shift+up") == "Shift+\u2191"

    def test_simple_letter(self) -> None:
        assert key_label("q") == "q"

    def test_arrow_keys(self) -> None:
        assert key_label("up") == "\u2191"
        assert key_label("down") == "\u2193"
        assert key_label("left") == "\u2190"
        assert key_label("right") == "\u2192"

    def test_ctrl_modifier(self) -> None:
        assert key_label("ctrl+s") == "Ctrl+s"

    def test_uppercase_letter(self) -> None:
        assert key_label("A") == "A"
