"""The optimizer CLIs preflight OPENROUTER_API_KEY and exit with setup help, not a mid-run 401."""
import pytest

from optimize import require_openrouter_key


def test_missing_key_exits_with_setup_help(monkeypatch, capsys):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        require_openrouter_key()
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "OPENROUTER_API_KEY" in err
    assert ".env.example" in err
    assert "openrouter.ai/keys" in err


def test_blank_key_is_treated_as_missing(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "   ")
    with pytest.raises(SystemExit):
        require_openrouter_key()


def test_set_key_passes(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    require_openrouter_key()  # no exit
