# Session log — 2026-07-17

## Objective

Harden the public repository for launch without changing the shared HIGH-impact GEPA promotion path.

## Changes

- Made agent-authored `create_skill` writes default-off behind
  `ENABLE_AGENT_SKILL_WRITES=1`.
- Preserved the existing trusted-local live-write behavior when explicitly enabled.
- Added tests for default refusal and opt-in creation.
- Passed the flag into the MCP Compose service and documented it in `.env.example`.
- Reconciled README, agent prompt, router docs, and safety docs with the new trust boundary.
- Added `SECURITY.md`, `CONTRIBUTING.md`, and GitHub bug/feature/security routing.
- Added implementation design and plan under `docs/superpowers/`.

## Decisions

- Did not modify `optimize.promote.promote`; GitNexus rated that shared path HIGH before work.
- Used a default-off MCP gate as the smallest reversible launch safeguard.
- CodeScene MCP v1.4.0 now runs through `op run` using the custom `PAT` field in the 1Password item
  `Slancha/Codescene PAT`; no token is stored in Codex config. The reference template lives at
  `~/.config/codescene-mcp/.env.op`.
- GitNexus post-change detection reports HIGH because seven `create_skill` flows are affected. This
  was acknowledged by Paul before commit even though the earlier symbol impact report was LOW.

## Verification

- `docker compose config --quiet`: passed.
- `docker compose build`: passed; `ingot-mcp` image SHA begins `943259a1`.
- Full Docker suite: `263 passed, 1 skipped, 1 warning in 16.50s`.
- `git diff --check`: passed.
- CodeScene installation: 4/4 checks passed (repository, token authentication, CLI connectivity,
  runtime).
- CodeScene `pre_commit_code_health_safeguard`: `quality_gates: passed`, no regressions.
- Retired launch-pair and unsafe-write claim scans: no stale public claim pair or unqualified
  live-write language found. Remaining isolated `0.05` / `10x` values describe unrelated routing,
  thresholds, or cost comparisons.

## Artifacts

- `SECURITY.md` — reporting and deployment trust boundaries.
- `CONTRIBUTING.md` — Docker development and pull-request gate.
- `.github/ISSUE_TEMPLATE/` — public bug, feature, and private security routes.
- `docs/superpowers/specs/2026-07-17-safe-agent-authoring-launch-design.md` — approved design.
- `docs/superpowers/plans/2026-07-17-safe-agent-authoring-launch.md` — implementation plan.

## Remaining blockers

1. Review and merge occur on `launch/human-gated-skills`; this session does not merge.
2. Fresh-clone verification runs against the exact merged candidate commit.
