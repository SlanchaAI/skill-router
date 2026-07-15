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


def test_improve_is_first_class_cli_workflow(monkeypatch):
    from optimize import ab
    called = []
    monkeypatch.setattr(ab, "run_ab", lambda skill, **kwargs: called.append((skill, kwargs)) or {})
    assert main(["improve", "pdf", "--budget", "12"]) == 0
    assert called == [("pdf", {"budget": 12})]


def test_review_prints_behavioral_gate(tmp_path, monkeypatch, capsys):
    from optimize import promote as promotion
    monkeypatch.setattr(promotion, "PENDING_DIR", tmp_path)
    promotion.save_pending("pdf", {"skill": "pdf", "gate": {"promotable": False, "blocked": ["regression"]},
                                   "evidence_paths": {"json": "evidence.json"}})
    assert main(["review", "pdf", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["gate"]["promotable"] is False
    assert payload["evidence_paths"]["json"] == "evidence.json"


def test_promote_cli_invokes_explicit_promotion(monkeypatch, capsys):
    from optimize import promote as promotion
    monkeypatch.setattr(promotion, "promote", lambda skill: f"promoted {skill}")
    assert main(["promote", "pdf"]) == 0
    assert "promoted pdf" in capsys.readouterr().out
