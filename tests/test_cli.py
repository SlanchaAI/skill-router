import json

from mcp_server.cli import main


def _write_skill(root):
    d = root / "pdf"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: pdf\ndescription: Merge PDF files.\n---\nPDF body\n")


def test_index_prints_revisioned_skill_count(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("SKILL_ROUTER_CACHE", str(tmp_path / "index.json"))
    _write_skill(tmp_path)
    assert main(["index", str(tmp_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["skills"] == 1 and payload["roots"] == [str(tmp_path.resolve())]


def test_route_json_matches_runtime_schema(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("SKILL_ROUTER_CACHE", str(tmp_path / "index.json"))
    _write_skill(tmp_path)
    code = main(["route", "merge two PDFs", "--root", str(tmp_path), "--harness", "codex",
                 "--min-score", "0", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["match"] == "pdf" and payload["skill_body"] == "PDF body"
    assert len(payload["revision"]) == 64
