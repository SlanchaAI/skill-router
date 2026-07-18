# Safe Agent Authoring Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make agent-authored skill writes explicitly opt-in and add the public security and contributor surfaces required for launch.

**Architecture:** Preserve the `create_skill` MCP contract, but fail closed before validation or filesystem mutation unless `ENABLE_AGENT_SKILL_WRITES=1`. Leave the HIGH-impact shared promotion path unchanged. Document the trust boundary and give contributors usable issue paths.

**Tech Stack:** Python 3.12, FastMCP 3, Docker Compose, pytest, Markdown, GitHub issue forms.

## Global Constraints

- Run all tests in the `ingot-mcp` Docker image.
- Do not change `optimize.promote.promote` without separate HIGH-impact acknowledgment.
- Existing opt-in creation behavior must remain byte-for-byte compatible after the flag gate.
- Public claims must match the current Excel tutorial evidence.

---

### Task 1: Default-off agent skill writes

**Files:**
- Modify: `tests/test_server.py`
- Modify: `mcp_server/server.py`
- Modify: `.env.example`

**Interfaces:**
- Preserves: `create_skill(name: str, description: str, body: str) -> str`
- Adds: `ENABLE_AGENT_SKILL_WRITES`, false unless exactly one of `1`, `true`, `yes`, `on`

- [ ] **Step 1: Write failing default-off and opt-in tests**

```python
def test_create_skill_is_disabled_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "SKILLS_DIR", tmp_path)
    monkeypatch.setattr(server, "ENABLE_AGENT_SKILL_WRITES", False)
    result = server.create_skill("new-skill", "Use this for new work.", "Do the work.")
    assert "disabled" in result.lower()
    assert not (tmp_path / "new-skill").exists()

def test_create_skill_opt_in_preserves_live_write(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "SKILLS_DIR", tmp_path)
    monkeypatch.setattr(server, "ENABLE_AGENT_SKILL_WRITES", True)
    monkeypatch.setattr(server.STATE.router, "nearest", lambda _: (None, 0.0))
    monkeypatch.setattr(server.STATE, "reload", lambda: 1)
    result = server.create_skill("new-skill", "Use this for new work.", "Do the work.")
    assert "Created skill" in result
    assert (tmp_path / "new-skill" / "SKILL.md").exists()
```

- [ ] **Step 2: Run tests and verify expected default-off failure**

Run: `docker run --rm -v "$PWD:/app" -w /app ingot-mcp python -m pytest tests/test_server.py -q`

Expected: default-off test fails because `ENABLE_AGENT_SKILL_WRITES` does not exist.

- [ ] **Step 3: Add the minimal flag and early return**

```python
ENABLE_AGENT_SKILL_WRITES = os.environ.get("ENABLE_AGENT_SKILL_WRITES", "").lower() in {
    "1", "true", "yes", "on",
}

def create_skill(...):
    if not ENABLE_AGENT_SKILL_WRITES:
        return ("Agent-authored skill writes are disabled. Set ENABLE_AGENT_SKILL_WRITES=1 "
                "only in a trusted local environment, or add the skill through human review.")
```

- [ ] **Step 4: Run targeted tests and full server/security tests**

Run: `docker run --rm -v "$PWD:/app" -w /app ingot-mcp python -m pytest tests/test_server.py tests/test_security.py -q`

Expected: all selected tests pass.

- [ ] **Step 5: Document the opt-in in `.env.example`**

Add a disabled-by-default security section with `# ENABLE_AGENT_SKILL_WRITES=1` and its trusted-local warning.

- [ ] **Step 6: Commit**

```bash
git add mcp_server/server.py tests/test_server.py .env.example
git commit -m "security: disable agent skill writes by default"
```

### Task 2: Public security and contributor funnel

**Files:**
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`
- Create: `.github/ISSUE_TEMPLATE/bug.yml`
- Create: `.github/ISSUE_TEMPLATE/feature.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Modify: `README.md`

**Interfaces:**
- Produces: public vulnerability-reporting and contribution entry points

- [ ] **Step 1: Add `SECURITY.md`**

Document supported branch, private reporting route, localhost/no-auth boundary, default-off agent
writes, opt-in classifier limitations, third-party skill trust, execution sandbox, and secret hygiene.

- [ ] **Step 2: Add `CONTRIBUTING.md` and issue forms**

Document Docker-only setup, test command, focused PR expectations, README-number provenance, and
security-report routing. Bug and feature forms must request reproduction/goal, environment, and
verification evidence without collecting secrets.

- [ ] **Step 3: Update README write-path and contribution copy**

Replace every statement that agent-authored skills activate by default. Explain the opt-in flag,
retain the safety checks as defense-in-depth, and link `SECURITY.md` plus `CONTRIBUTING.md`.

- [ ] **Step 4: Run literal consistency scan**

Run: `rg -n "goes live with no human approval|live immediately|persist its solution|grows exactly" README.md mcp_server agent .env.example SECURITY.md CONTRIBUTING.md`

Expected: code/prompt occurrences are either removed or explicitly qualified by the opt-in flag.

- [ ] **Step 5: Commit**

```bash
git add SECURITY.md CONTRIBUTING.md .github README.md
git commit -m "docs: add launch security and contributor paths"
```

### Task 3: Branch verification

**Files:**
- Modify only files required by failed verification.

**Interfaces:**
- Produces: push-ready public hardening branch

- [ ] **Step 1: Build current Docker image**

Run: `docker compose build`

Expected: all project images build.

- [ ] **Step 2: Run full tests**

Run: `docker run --rm -v "$PWD:/app" -w /app ingot-mcp python -m pytest tests -q`

Expected: no failures.

- [ ] **Step 3: Validate Compose and scan claims**

Run: `docker compose config --quiet`

Run: `rg -n "0\.05|0\.525|16/23|1,072|750|10×|10x" README.md SECURITY.md CONTRIBUTING.md`

Expected: Compose exits 0; no retired public launch claims.

- [ ] **Step 4: Run CodeScene pre-commit safeguard and GitNexus change detection**

Expected: no Code Health regression and no unreviewed HIGH/CRITICAL impact.

- [ ] **Step 5: Commit verification/session log and push branch**

```bash
git add SESSION_LOG_2026_07_17.md docs/superpowers
git commit -m "docs: record launch hardening verification"
git push -u origin launch/human-gated-skills
```
