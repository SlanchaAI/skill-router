"""Local-first command line interface for indexing, routing, and serving skills."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .registry import configured_roots, load_skills
from .router import Router


def _cache_path() -> Path:
    override = os.environ.get("SKILL_ROUTER_CACHE")
    return Path(override).expanduser() if override else Path.home() / ".cache" / "skill-router" / "index.json"


def _write_index(roots: list[Path], skills) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"roots": [str(root) for root in roots],
               "skills": [{"name": skill.name, "revision": skill.revision} for skill in skills]}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n")
    tmp.replace(path)


def _indexed_roots() -> list[Path] | None:
    path = _cache_path()
    if not path.exists():
        return None
    try:
        return [Path(root) for root in json.loads(path.read_text())["roots"]]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise SystemExit(f"corrupt index at {path}; rerun skill-router index")


def _roots(explicit) -> list[Path]:
    return configured_roots(explicit if explicit else _indexed_roots())


def _print(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
    elif payload.get("match"):
        print(f"{payload['match']}  score={payload['score']:.3f}  revision={payload['revision']}")
        print(payload["reason"])
    else:
        print(f"no match: {payload.get('reason', 'unknown reason')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-router", description="Route to and improve Agent Skills")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="validate and remember external skill roots")
    index.add_argument("roots", nargs="+")
    index.add_argument("--json", action="store_true")

    route = commands.add_parser("route", help="select and load one compatible skill")
    route.add_argument("task")
    route.add_argument("--root", action="append", default=[])
    route.add_argument("--harness", choices=["claude", "codex"], default="codex")
    route.add_argument("--cwd", default=os.getcwd())
    route.add_argument("--tool", action="append", default=[])
    route.add_argument("--mcp", action="append", default=[])
    route.add_argument("--platform")
    route.add_argument("--min-score", type=float, default=float(os.environ.get("MIN_SCORE", "0.65")))
    route.add_argument("--json", action="store_true")

    serve_parser = commands.add_parser("serve", help="serve the one-tool MCP router")
    serve_parser.add_argument("--root", action="append", default=[])
    transport = serve_parser.add_mutually_exclusive_group()
    transport.add_argument("--stdio", action="store_true", default=True)
    transport.add_argument("--http", action="store_true")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    doctor = commands.add_parser("doctor", help="report routing configuration without changing it")
    doctor.add_argument("--root", action="append", default=[])
    doctor.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "index":
        roots = configured_roots(args.roots)
        skills = load_skills(roots=roots)
        Router(skills)
        _write_index(roots, skills)
        payload = {"roots": [str(root) for root in roots], "skills": len(skills)}
        _print(payload, args.json)
        return 0
    if args.command == "route":
        skills = load_skills(roots=_roots(args.root))
        payload = Router(skills).route(args.task, args.harness, args.cwd, args.tool, args.mcp,
                                       args.platform, args.min_score)
        _print(payload, args.json)
        return 0
    if args.command == "serve":
        from .server import serve
        serve(stdio=not args.http, host=args.host, port=args.port, roots=_roots(args.root))
        return 0
    roots = _roots(args.root)
    skills = load_skills(roots=roots)
    payload = {"ok": True, "roots": [str(root) for root in roots], "skills": len(skills),
               "default_transport": "stdio", "model_facing_tools": ["route_and_load"]}
    _print(payload, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
