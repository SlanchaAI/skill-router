"""Read-only MCP surface for selecting and loading one compatible Agent Skill."""
from __future__ import annotations

import os
import threading
from pathlib import Path

from fastmcp import FastMCP

from .registry import configured_roots, load_skills
from .router import Router

MIN_SCORE = float(os.environ.get("MIN_SCORE", "0.65"))


class _State:
    def __init__(self):
        self._lock = threading.RLock()

    @staticmethod
    def _signature(roots) -> tuple:
        files = []
        for root in roots:
            files.extend(root.glob("*/SKILL.md"))
            files.extend(root.glob("*/variants/*.md"))
        return tuple((str(path.resolve()), path.stat().st_mtime_ns, path.stat().st_size)
                     for path in sorted(files))

    def reload(self, roots=None) -> int:
        selected_roots = configured_roots(roots)
        skills = load_skills(roots=selected_roots)
        router = Router(skills)
        signature = self._signature(selected_roots)
        with self._lock:
            self.roots, self.skills, self.router = selected_roots, skills, router
            self.signature = signature
            return len(self.skills)

    def refresh_if_changed(self) -> None:
        with self._lock:
            roots, prior = list(self.roots), self.signature
        if self._signature(roots) != prior:
            self.reload(roots)


STATE = _State()
STATE.reload()
mcp = FastMCP("skill-router")


@mcp.tool()
def route_and_load(task: str, harness: str, cwd: str, available_tools: list[str] | None = None,
                   available_mcps: list[str] | None = None) -> dict:
    """Select one compatible skill for a task and return its instructions, or return no match."""
    STATE.refresh_if_changed()
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
