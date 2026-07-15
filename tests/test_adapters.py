import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLAUDE = ROOT / "adapters" / "claude"
CODEX = ROOT / "adapters" / "codex" / "skill-router"


def _body(path):
    text = path.read_text()
    return text.split("---", 2)[-1].strip()


def test_codex_plugin_manifest_and_components_are_valid_shape():
    manifest = json.loads((CODEX / ".codex-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "skill-router"
    assert manifest["version"] == "0.2.0"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert len(list((CODEX / "skills").glob("*/SKILL.md"))) == 1


def test_adapters_start_same_stdio_server():
    claude = json.loads((CLAUDE / "mcp.json").read_text())["mcpServers"]["skill-router"]
    codex = json.loads((CODEX / ".mcp.json").read_text())["mcpServers"]["skill-router"]
    assert claude == codex == {"command": "skill-router", "args": ["serve", "--stdio"]}


def test_bootstraps_are_tiny_and_never_request_catalog_dump():
    paths = [CLAUDE / "skill-router" / "SKILL.md", CODEX / "skills" / "skill-router" / "SKILL.md"]
    for path in paths:
        body = _body(path)
        assert len(body.split()) < 150
        assert "route_and_load" in body
        assert "list_skills" not in body
        assert "catalog" in body.lower()
        assert "no match" in body.lower()


def test_bootstrap_policy_differs_only_by_harness_name():
    claude = _body(CLAUDE / "skill-router" / "SKILL.md").replace("`claude`", "`HARNESS`")
    codex = _body(CODEX / "skills" / "skill-router" / "SKILL.md").replace("`codex`", "`HARNESS`")
    assert claude == codex
