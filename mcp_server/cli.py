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

    improve = commands.add_parser("improve", help="mine, propose, and behaviorally gate a challenger")
    improve.add_argument("skill")
    improve.add_argument("--budget", type=int, default=60)

    review = commands.add_parser("review", help="inspect a quarantined challenger and its evidence")
    review.add_argument("skill")
    review.add_argument("--json", action="store_true")

    promote = commands.add_parser("promote", help="explicitly promote a challenger that passed its gate")
    promote.add_argument("skill")

    evaluate = commands.add_parser("eval", help="run held-out routing cases")
    evaluate.add_argument("suite")
    evaluate.add_argument("--root", action="append", default=[])
    evaluate.add_argument("--min-score", type=float, default=float(os.environ.get("MIN_SCORE", "0.65")))
    evaluate.add_argument("--json", action="store_true")

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
    if args.command == "improve":
        try:
            from optimize.ab import run_ab
        except ImportError as exc:
            raise SystemExit("improvement dependencies missing; install skill-router[optimizer]") from exc
        summary = run_ab(args.skill, budget=args.budget)
        if summary.get("evidence_paths"):
            print(summary["evidence_paths"]["markdown"])
        return 0
    if args.command == "review":
        from optimize.promote import load_pending
        pending = load_pending(args.skill)
        if not pending:
            raise SystemExit(f"no pending challenger for '{args.skill}'")
        payload = {"skill": args.skill, "gate": pending.get("gate", {}),
                   "changed_components": pending.get("changed_components", []),
                   "evidence_paths": pending.get("evidence_paths", {})}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            state = "PASS" if payload["gate"].get("promotable") else "BLOCKED"
            print(f"{args.skill}: {state}")
            for reason in payload["gate"].get("blocked", []):
                print(f"- {reason}")
            if payload["evidence_paths"].get("markdown"):
                print(payload["evidence_paths"]["markdown"])
        return 0
    if args.command == "promote":
        from optimize.promote import promote
        print(promote(args.skill))
        return 0
    if args.command == "eval":
        from .routing_eval import evaluate_cases, load_cases
        result = evaluate_cases(Router(load_skills(roots=_roots(args.root))),
                                load_cases(Path(args.suite)), min_score=args.min_score)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"top1={result['top1']:.3f} recall@3={result['recall_at_3']:.3f} "
                  f"no-route={result['no_route_precision']:.3f} failures={len(result['failures'])}")
        return 0 if not result["failures"] else 1
    if args.command == "doctor":
        roots = _roots(args.root)
        unavailable = [str(root) for root in roots if not root.is_dir()]
        native = {}
        for harness, directory in {
            "claude": Path.home() / ".claude" / "skills",
            "codex": Path.home() / ".codex" / "skills",
        }.items():
            native[harness] = sum(1 for path in directory.glob("*/SKILL.md")
                                  if path.parent.name != "skill-router")
        issues = [f"unavailable root: {root}" for root in unavailable]
        issues.extend(f"{count} non-bootstrap native {harness} skill(s) remain"
                      for harness, count in native.items() if count)
        skills = load_skills(roots=roots) if not unavailable else []
        payload = {
            "ok": not issues,
            "roots": [str(root) for root in roots],
            "skills": len(skills),
            "native_catalogs": native,
            "default_transport": "stdio",
            "model_facing_tools": ["route_and_load"],
            "issues": issues,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print("ok" if payload["ok"] else "configuration needs attention")
            for issue in issues:
                print(f"- {issue}")
        return 0 if payload["ok"] else 1
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
