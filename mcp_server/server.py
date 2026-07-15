"""Read-only MCP surface for selecting and loading one compatible Agent Skill."""
from __future__ import annotations

import os
from pathlib import Path

from fastmcp import FastMCP

from .registry import configured_roots, load_skills
from .router import Router

MIN_SCORE = float(os.environ.get("MIN_SCORE", "0.65"))


class _State:
    def reload(self, roots=None) -> int:
        self.roots = configured_roots(roots)
        self.skills = load_skills(roots=self.roots)
        self.router = Router(self.skills)
        return len(self.skills)


STATE = _State()
STATE.reload()
mcp = FastMCP("skill-router")


@mcp.tool()
def route_and_load(task: str, harness: str, cwd: str, available_tools: list[str] | None = None,
                   available_mcps: list[str] | None = None) -> dict:
    """Select one compatible skill for a task and return its instructions, or return no match."""
    return STATE.router.route(task, harness, cwd, available_tools or [], available_mcps or [],
                              min_score=MIN_SCORE)


def serve(*, stdio: bool = True, host: str = "127.0.0.1", port: int = 8000,
          roots: list[str | Path] | None = None) -> None:
    STATE.reload(roots)
    if stdio:
        mcp.run(transport="stdio")
        return
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("non-loopback HTTP is disabled; use stdio or bind 127.0.0.1")
    mcp.run(transport="http", host=host, port=port, path="/mcp")


if __name__ == "__main__":
    from .cli import main
    raise SystemExit(main(["serve"]))
