# Safe Agent Authoring Launch Design

## Decision

Disable agent-authored live writes by default for launch. Keep the `create_skill` MCP interface so
existing agents remain compatible, but require `ENABLE_AGENT_SKILL_WRITES=1` before it can mutate the
skill library. This is the low-risk fallback approved after GitNexus rated changes to the shared
promotion path HIGH impact.

The durable design remains a unified approval queue for agent-authored and optimized skills. That
requires a separately acknowledged change to `optimize.promote.promote`, its UI caller, optimizer
loop, and canary callers. This launch-hardening branch does not change those interfaces.

## Behavior

- Default: `create_skill` validates nothing, writes nothing, and returns an actionable disabled
  message.
- Opt-in: `ENABLE_AGENT_SKILL_WRITES=1` preserves the existing validation, collision checks, write,
  and hot reload behavior.
- The MCP tool remains registered in both modes.
- Public documentation describes opt-in creation as an experimental trusted-local mode, not a
  human-gated or production-safe path.

## Public launch surfaces

- Add `SECURITY.md` with write-path, network, model, and reporting guidance.
- Add `CONTRIBUTING.md` and issue templates so launch traffic has a real contributor path.
- Keep README proof anchored to the current reproducible Excel tutorial. Do not reintroduce the
  retired PDF 10x/token-saving launch claims.

## Verification

- TDD proves default refusal creates no directory and explicit opt-in preserves creation.
- Full Docker pytest suite passes.
- Compose configuration renders.
- Literal scan finds no public claim that agent-authored skills activate by default.
