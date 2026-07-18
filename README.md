# Ingot

**Mine your traffic. Refine your skills.**

<p align="center">
  <img src="docs/ingot.jpg" alt="Ingot, the mascot, handing skills out to AI agents" width="720">
</p>

**Ingot** is a self-improving [Agent Skills](https://github.com/anthropics/skills) library. An **MCP server**
routes tasks to skills by embedding similarity and serves them to a **LangGraph deep agent**; every
run is traced to a self-hosted **[Langfuse](https://langfuse.com)**; a **[GEPA](https://github.com/gepa-ai/gepa)
optimizer** mines the traces for failures, rewrites a failing skill, and **A/B-tests champion vs
challenger through the full agent** on held-out tasks; you review the diff and scores in a small
**approval UI**, and the winner goes live via hot reload — no restart.

## Privacy first

**Privacy focused throughout** — three properties, all defaults, none optional:

- **Zero data retention LLM calls.** The default provider is **Fireworks AI**, which is
  [zero-data-retention by default](https://docs.fireworks.ai/guides/security_compliance/data_handling)
  for open models on serverless — "Fireworks does not log or store prompt or generation data for
  any open models, without explicit user opt-in" (prompts exist only in volatile memory; see also
  their [privacy policy](https://fireworks.ai/privacy-policy)). Point `BASE_URL` at **OpenRouter**
  instead and every request — agent runs, GEPA rollouts and reflection, the judge, task
  drafting — carries a hardcoded provider preference:

  ```json
  {"provider": {"zdr": true, "data_collection": "deny"}}
  ```

  OpenRouter then routes only to **zero-data-retention endpoints** operated by providers that do
  not collect user data; a model with no qualifying endpoint fails loudly rather than falling back
  to one that retains prompts.
- **Self-hosted tracing.** Langfuse (and its Postgres / ClickHouse / MinIO) runs inside the compose
  stack — traces, skill contents, and eval outputs never leave your machine.
- **Localhost only.** No service is reachable off the machine
  (see [Network exposure](#network-exposure)).

The only data that leaves your machine is the LLM traffic itself, under ZDR — and the endpoint is
yours to choose: `BASE_URL` + `API_KEY` point everything at **any OpenAI-compatible provider**
(`MODEL_BASE_URL`/`MODEL_API_KEY` override just the serving role for hybrid setups):

```bash
# the default (.env.example): Fireworks AI direct — ZDR for open models on serverless
BASE_URL=https://api.fireworks.ai/inference/v1
API_KEY=fw_...
AGENT_MODEL=accounts/fireworks/models/qwen3p7-plus
GEPA_MODEL=accounts/fireworks/models/glm-5p2
JUDGE_MODEL=accounts/fireworks/models/deepseek-v4-pro

# fully local (no key needed at all): everything on Ollama / vLLM
BASE_URL=http://172.17.0.1:11434/v1  AGENT_MODEL=qwen3:32b  GEPA_MODEL=qwen3:32b  JUDGE_MODEL=llama3.3:70b
```

The hardcoded ZDR provider preference applies to OpenRouter endpoints; provider-direct endpoints
get a clean OpenAI-compatible request under that vendor's own retention policy (Fireworks: ZDR by
default, as above), and local endpoints are the strongest privacy of all. No API key is required when nothing points at a hosted
endpoint. From inside the compose containers, "localhost" is the container — use your host's LAN
IP (or `172.17.0.1` on Linux).

## Tutorial

The tutorial runs the whole improvement loop on a skill you write yourself, and the arc is the
product's honest pitch: **write the quick first-draft skill you'd actually jot down, watch it
under-deliver on real traffic, and let the system mature it** — content and routing, each measured
by its own metric, each change gated and human-approved. Every command, number, and screenshot
below comes from a real run; nothing is mocked.

### 1. Set up and start the stack

```bash
git clone https://github.com/SlanchaAI/ingot.git && cd ingot
cp .env.example .env               # put your Fireworks key in it (https://fireworks.ai/account/api-keys)
scripts/fetch_skills.sh all        # fetch ~70 real skills into ./skills (see Skill sources)
docker compose up --build
```

This brings up the MCP server (`localhost:8000`), Langfuse (`localhost:3100`), the approval UI
(`localhost:8080`) — and runs the agent once on a demo task so you have something to look at.

No skills are committed to this repo — `fetch_skills.sh` clones each source, copies its skills in,
and deletes the clone, so everything stays under its own upstream license. Without an API key
everything still starts and the router still prints suggestions (the embedding router needs no
LLM); the agent and optimizer will tell you what to set and exit cleanly.

### 2. The agent routes to a skill and uses it

```bash
docker compose run --rm agent "How do I merge several PDFs into one and add page numbers?"
```

```
PROPOSED SKILLS (MCP suggest_skills):
    0.74  pdf — Use this skill whenever the user wants to do anything with PDF files...

SERVING MODEL: accounts/fireworks/models/qwen3p7-plus

LOADED SKILLS (MCP get_skill): ['pdf@83a75cf1f9b5…']
TOKENS: 23233 in / 698 out

RESULT:
... (working pypdf + reportlab code, following the loaded skill)
[agent] trace sent to Langfuse (http://localhost:3100)
```

The agent asked the router (`suggest_skills`), loaded the top match (`get_skill` — the `@…` suffix
is the skill's content-hash revision, which also lands on the trace as a tag), and followed it.
The `SERVING MODEL` line is the weak/strong split at work: a routed task runs on the cheap
`AGENT_MODEL` because the skill carries the method — only truly novel tasks escalate to
`STRONG_MODEL` (step 11).
Open **http://localhost:3100** (login `demo@local.dev` / `localdemo123` — local demo literals baked
into the compose file, not secrets) to see the full trace: every tool call, LLM call, and token count.
(Have a Langfuse project already? You can trace there instead — see
[Using your own Langfuse project](#using-your-own-langfuse-project).)

### 3. Write a first-draft skill — and watch it under-deliver

A skill is a directory with a `SKILL.md`: YAML frontmatter whose `description` is the routing key,
and a body the agent loads. The tutorial skill is **Tailwind CSS** — a real library with a hard
version break (v4, January 2025, moved configuration from `tailwind.config.js` into CSS), which
makes it a perfect stress test: the quick notes you'd actually jot down are not just thin, they're
*stale*. Write that first draft:

```bash
mkdir -p skills/tailwind
cat > skills/tailwind/SKILL.md <<'EOF'
---
name: tailwind
description: Use this skill when the user needs help with Tailwind CSS.
---

# Tailwind CSS

1. Install with npm and run the init command to create tailwind.config.js.
2. Add your source files to the `content` array so classes are picked up.
3. Put custom colors, fonts, and breakpoints under `theme.extend`.
4. Start your CSS with `@tailwind base;` `@tailwind components;` `@tailwind utilities;`.
EOF
```

(Every line of that body is the v3 way — i.e., wrong since v4. That's not sabotage, that's what
old notes look like.) `skills/` is bind-mounted and the server hot-reloads on change — the skill
is live immediately. Now send it some realistic traffic:

```bash
for t in "Add a brand color to my Tailwind setup so bg-brand works." \
         "Set up Tailwind in a fresh Vite app." \
         "Why aren't the classes from my component library in node_modules getting styled?"; do
  docker compose run --rm agent "$t"
done
```

```
== Add a brand color to my Tailwind setup so bg-brand works.
PROPOSED SKILLS (MCP suggest_skills):
   0.723  tailwind — Use this skill when the user needs help with Tailwind CSS.
LOADED SKILLS (MCP get_skill): (none)
== Set up Tailwind in a fresh Vite app.
PROPOSED SKILLS (MCP suggest_skills):
   0.709  tailwind — Use this skill when the user needs help with Tailwind CSS.
LOADED SKILLS (MCP get_skill): ['tailwind@77156f5efe1a…']
== Why aren't the classes from my component library in node_modules getting styled?
PROPOSED SKILLS (MCP suggest_skills):
   0.621  web-artifacts-builder (related — compose/extend) — Suite of tools for creating elaborate…
LOADED SKILLS (MCP get_skill): (none)
```

Three requests, three different failures. The requests that *say* "Tailwind" route fine — and the
second one actually **loaded the skill**, meaning live traffic was just served the stale v3 notes.
The third request — a Tailwind problem that never says Tailwind — misrouted to a different skill
entirely (`web-artifacts-builder` mentions Tailwind in its description, so it wins on vocabulary).
All three failures are now sitting in your traces.

### 4. Mine what's failing (from real traces)

`optimize-mine` re-judges your logged traffic with a multi-dimensional LLM judge and aggregates
which failure dimensions dominate — the [SkillForge paper's](https://arxiv.org/abs/2604.08618)
"Failure Analyzer" applied to your own traces. Only traces relevant to the skill are counted:
tagged with it, or ranking it in the embedding top-5 for the task text — so misrouted traffic
still counts toward the skill that *should* have served it:

```bash
docker compose run --rm optimize-mine tailwind
```

```
[mine] pulling recent traces from Langfuse for 'tailwind'…
[mine] 39/50 recent traces relevant to 'tailwind' (tagged with it, or ranking it in the embedding top-5)
[mine] analyzed 39 real traces · mean judge score 0.50 · 20 bad cases (score < 0.5)
[mine] failure dimensions (paper's Failure Analyzer), most common first:
    correctness             20/39  █████
        · 'Set up Tailwind in a fresh Vite app.' → Missing postcss and autoprefixer dependencies and postcss.config.js
        · 'Set up Tailwind CSS v4 in a project bundled with plain PostCSS (no Vit' → Uses v3 directives and config, not v4 API.
    completeness            20/39  █████
        · 'Set up Tailwind in a fresh Vite app.' → Incomplete: essential PostCSS configuration is absent
    instruction_following   20/39  █████
        · 'Set up Tailwind CSS v4 in a project bundled with plain PostCSS (no Vit' → Ignores rubric: uses @tailwind directives and tailwind.config.js.
    efficiency              16/39  ████
        · 'Set up Tailwind CSS v4 in a project bundled with plain PostCSS (no Vit' → Includes unnecessary tailwind.config.js and v3-specific steps.
[mine] 6 weakest tasks mined as eval candidates → optimize on these next.
```

The diagnosis is version drift, named per dimension: answers built on `tailwind.config.js` and
`@tailwind` directives — the v3 world the stub teaches and pretraining reinforces. The weakest
mined tasks are also surfaced as eval candidates: real traffic is the best source of train/holdout
tasks for `optimize/tasks/<skill>.yaml`, and the eval set used below was built exactly that way —
see [Writing eval task sets](#writing-eval-task-sets) for the format and the full annotated example.

(Reference-free judging of live traffic is noisier than rubric-based judging — treat mined
dimensions as a diagnosis to investigate, not a verdict. The optimizer's own gate runs on rubrics.)

### 5. Optimize the body: parallel candidates + a held-out A/B

Write an eval task set for the skill (`optimize/tasks/tailwind.yaml`) — train and holdout tasks
whose rubrics carry the v4 ground truth, built from the mined traffic above; the format, and the
rules that make a set worth gating on, are in [Writing eval task sets](#writing-eval-task-sets)
(for a quick start, the teacher can also **auto-draft** one: any CLI optimize run on a skill with
no task set drafts train/holdout tasks first and persists them). Then open the approval UI at
**http://localhost:8080** — the **Skills** list shows every skill the router serves, and skills
with a task set carry an `evals` chip — and click **Optimize**, watching the optimizer log stream
on the page. The optimizer authors several candidate bodies in parallel (the teacher model, each
steered by a different angle), races them on the train tasks — successive halving, every wave
fully concurrent — and A/Bs the winner against the champion through the full agent on the
held-out tasks (a few minutes, well under $1; the serving-side A/B injects each variant body, so
the comparison is exactly body vs body). Repeat runs are cheaper still: the champion's held-out
scores are cached by revision. See [Optimization strategies](#optimization-strategies) for the
design — and for the slower GEPA reflective loop it replaced as default (`--gepa`). The same run
also works headless (`docker compose run --rm optimize tailwind`). Our run:

```
[bestofn] optimizing 'tailwind' (components: ['body']; frozen: ['description']) on 6 train tasks (parallel best-of-N + racing)…
[bestofn] seed scores 0.050 on 6 train tasks; authoring 5 candidates in parallel…
[bestofn] race round 1/6 (Set up Tailwind CSS v4 in a Vite project — what do…): 3 candidate(s) advance, 2 dropped
[bestofn] race round 2/6 (Add a custom color `brand` (#7c3aed) in Tailwind v…): 2 candidate(s) advance, 1 dropped
[bestofn] race round 3/6 (How does Tailwind v4 decide which files to scan fo…): 2 candidate(s) advance
[bestofn] race round 6/6 (My v3 markup uses `shadow-sm` and `rounded-sm`, an…): 2 candidate(s) advance
[bestofn] winner: candidate 1 at 0.967 (seed 0.050)
[opt] inner-loop score: seed 0.050 -> best 0.967
[ab] evaluating champion vs challenger on 6 held-out tasks…
[ab] champion: mean judge score 1.000  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
[ab] challenger: mean judge score 0.833  [1.0, 0.0, 1.0, 1.0, 1.0, 1.0]
[ab] champion 1.000 vs challenger 0.833 -> champion holds
[ab] champion holds — nothing to promote.
```

Read the two halves of that log separately, because they teach different things. The **inner loop**
did its job: served through the stub in a bare rollout, the model scored 0.050 — and the authors,
briefed with the rubrics and the seed's failures, distilled a v4-era body scoring 0.967 in about
two minutes. But the **held-out A/B runs through the full agent**, and there the champion scored a
perfect 1.000: a frontier serving model, given room to reason, recognizes the stub's v3 advice as
stale and answers v4 from its own knowledge. The rewrite could only match it (its one 0.0 was a
runaway loop on one task), so the gate refused the swap. *No measurable win, no challenger.*

That result generalizes, and it's worth being direct about: **body-pass wins concentrate where the
body carries knowledge the serving model can't have** — your internal tools, your conventions,
your post-cutoff dependencies — exactly the rubric-distillation workflow described in
[Writing eval task sets](#writing-eval-task-sets). On public-knowledge domains, strong models
transcend bad bodies (and much weaker models can fail to follow *any* body buried in a large agent
scaffold — we measured both edges). The gate's refusals are the feature that makes the wins
trustworthy: in a companion run against the NVIDIA-authored `accelerated-computing-cudf` skill,
the challenger dropped half the champion body and regressed a held-out task — blocked, 0.980 vs
0.800. What *this* stub measurably lacks is routing — next step.

**Optimization is greedy — one component per pass, each scored by its own role's metric:**

| pass | command | inner-loop objective | cost |
|------|---------|---------------------|------|
| body (default) | the UI's **Optimize** button, or `optimize tailwind` | LLM judge on train tasks; full-agent A/B gate | ~$0.3 (`--gepa`: ~$1) |
| description | `optimize tailwind --description` | the **routing suite**, scored by the real embedding router — no LLM rollouts (reflection only) | ~$0.05, seconds |
| scripts | `optimize tailwind --scripts` | refused for now: bundled scripts need execution-grounded evals before a rewrite can be measured | — |

This split exists because a quality judge can't measure routing and a router can't measure quality;
letting one metric grade both components teaches the optimizer to hide behavioral rules in the
routing description (the routing-regression gate catches it, but better to make it impossible).
The body pass's rollouts serve each candidate under the **exact contract the A/B serves**, so the
inner loop can't optimize against different instructions than the outer loop measures — and
`GEPA_ROLLOUTS=agent` runs every rollout through the full agent scaffold when the failures you're
chasing live there (e.g. code written to a scratch file instead of the answer).

### 6. Fix the routing with the description pass

Step 3's third request — the one that never says "Tailwind" — misrouted, and the routing key is
the `description`, so routing gets its own pass with its own metric. It optimizes against the
`routing:` cases in `optimize/tasks/tailwind.yaml`: realistic positive phrasings plus
`expected: null` negatives. One lesson from our own run: our first suite's positives all contained
the word "Tailwind", the stub description already scored 0.833 on it, and the pass rightly
reported *champion holds* — a suite of phrasings that already route has no power to improve
anything. **The cases that matter are the real misses**, so put your mined traffic in the suite
(we added the node_modules request verbatim, plus a "classes disappear in the production build"
variant):

```bash
docker compose run --rm optimize tailwind --description
```

```
[routing] optimizing 'tailwind' description against 7 routing cases (budget 60 metric calls; inner loop is embedding-only — no LLM rollouts)…
[routing] inner-loop score: seed 0.571 -> best 0.857
[routing] champion: top1 0.600 · recall@3 0.600 · no-route precision 0.500
[routing] challenger: top1 1.000 · recall@3 1.000 · no-route precision 0.500
[routing] pending description written to /app/runs/pending/tailwind.json — review + promote at http://localhost:8080
```

Top-1 routing goes **0.600 → 1.000** in seconds, for a few reflection calls (~$0.03) — every
candidate description is scored by the real embedding router against the real skill corpus, so
there's nothing for an LLM judge to be fooled about. Look at what the winning description learned
to do: it names the *symptoms* users actually type ("unstyled classes from component libraries in
node_modules", "utility classes that work in dev but disappear in the production build") — and it
deliberately keeps v3 vocabulary like `tailwind.config.js`, because a routing description must
speak the words traffic uses, even outdated ones; the v4 truth lives in the body. The gate
requires no regression on any routing metric, at least one strict improvement, and no collision
with another skill's description. A scored challenger is now waiting for you in the UI.

### 7. Review and promote in the approval UI

Back at **http://localhost:8080**, the header pill flips to **1 to review**, a REVIEW alert
appears, and the `tailwind` row is highlighted with a `challenger ready` chip:

![approval UI — skills list with a challenger ready](docs/ui-home.png)

Click **Review challenger** (the pending review also opens automatically). For this routing
challenger the review shows the metric deltas, the gate verdict, and the description diff — a
body challenger shows judge scores, the token shift, and retention warnings the same way:

![approval UI — pending challenger review](docs/ui-review.png)

**Approve & promote** verifies the evidence still matches the on-disk champion and the exact
challenger, snapshots the prior revision, and swaps the challenger into `skills/tailwind/`.
The MCP server notices the revision change on its next request — the new description is served
with **no restart**. **Reject** discards it.

### 8. The same request now finds the skill

```bash
docker compose run --rm agent "Why aren't the classes from my component library in node_modules getting styled?"
```

```
PROPOSED SKILLS (MCP suggest_skills):
   0.661  tailwind — Use this skill when the user needs help with Tailwind CSS, including con…

SERVING MODEL: accounts/fireworks/models/qwen3p7-plus

LOADED SKILLS (MCP get_skill): ['tailwind@1b65da6e92f1…']
TOKENS: 28882 in / 1005 out
```

The exact request that misrouted in step 3 now clears the threshold, routes to `tailwind`, and the
agent loads the promoted revision (note the new `@…` hash). One honest caveat from our runs: on
trivially easy requests the serving model sometimes answers without bothering to load the matched
skill at all — the controlled body-vs-body comparison is the A/B in step 5, which guarantees
serving; live loading behavior is the serving model's own.

That's the loop: a first-draft skill → real traffic → mined diagnosis → a body pass gated on
held-out quality (which here correctly refused a rewrite the serving model didn't need) → a
description pass gated on routing metrics → human approval at every promotion → hot reload.

### 9. (Optional) Promote via a live canary instead

The offline A/B gates on a fixed held-out set. The production-honest alternative is a **canary**:
serve the challenger to a fraction of *live* traffic, judge each real outcome, and promote only
once the challenger's posterior beats the champion's:

```bash
docker compose run --rm optimize-canary pdf --epsilon 0.5
```

```
[canary] 'pdf': routing 50% of traffic to the challenger, judging each outcome (promote at P≥0.95, …)
[canary] req  4: challenger ok | served champ 2 / chall 2 | P(chall>champ)=0.50
[canary] req 21: challenger ok | served champ 13 / chall 8 | P(chall>champ)=0.89
[canary] req 23: champion   ·  | served champ 15 / chall 8 | P(chall>champ)=0.94
[canary] inconclusive after 24 requests (P=0.91) — keeping champion; raise --max/--epsilon for more samples.
```

Each request flips an ε-coin, the outcome is judged, each arm keeps a Beta posterior, and the run
stops early to promote (P≥0.95) or reject (P≤0.05). In this run the challenger climbed to P=0.91 —
likely better, but under the conservative bar — so the canary kept the champion rather than flip
production on borderline evidence. The gate is deliberately hard to trip. Add `--promote` to
auto-promote on a win; otherwise a win is recorded as a recommendation for the UI.

Every canary request is **first-class in Langfuse**: its trace is tagged with the arm and the exact
skill revision (`canary=challenger`, `revision=<hash>`), and the judged outcome is written back as
scores (`canary_judge`, `canary_success`) on that trace — so the per-arm evidence is auditable in
the Langfuse UI and the posterior can be recomputed from stored scores at any time.

### 10. (Optional) Put it on autopilot

One command mines every skill's real traffic for health and optimizes only the ones actually
failing, leaving every survivor in the approval UI (nothing auto-promotes):

```bash
docker compose run --rm optimize-loop            # all skills with eval sets; add names to target some
```

```
[loop] ===== pdf =====
[mine] analyzed 23 real traces · mean judge score 0.52 · 11 bad cases
[loop] pdf: below health bar (mean 0.52) — optimizing…
   … GEPA + held-out A/B + gate …
[loop] done. 1 challenger(s) passed the gate and are queued for review at http://localhost:8080: ['pdf']
```

Point it at your logged traffic on a schedule and skills that drift on your real workload get
re-optimized and queued for a human — continuously.

### 11. Grow the library

Three ways the library grows:

**Write one yourself** — exactly like step 3: a directory, a `SKILL.md`, and it's live on the next
request. Only two frontmatter fields matter: `name` (a slug) and `description` (the routing
trigger — write it "pushy", starting with "Use this skill when…", since under-triggering is the
common failure; and as step 7 showed, the description pass can fix it for you afterwards).

**Let the agent write one** — when `suggest_skills` returns an empty list (nothing even related),
the request escalates to `STRONG_MODEL` (defaults to `GEPA_MODEL`, the same teacher that rewrites
skills offline): it solves the task and persists what it learned via the `create_skill` MCP tool.
The new skill is distilled from a strong solution, and the next similar request routes to it on the
cheap `AGENT_MODEL`:

```bash
docker compose run --rm agent "Plan a strict low-FODMAP weekly dinner menu for two people"
# PROPOSED SKILLS (MCP suggest_skills):            <- empty: no skill covers this
# SERVING MODEL: accounts/fireworks/models/glm-5p2 (strong — no skill matched, will author one)
# ... solves the task ...
# mcp log: [ingot] created skill 'low-fodmap-meal-planning' — live immediately
```

How often this fires is governed by `RELATED_SCORE`: the nearest-skill similarity floor rises with
library size (with ~70 skills even unrelated tasks score ≈0.5 against their closest neighbor), so
raise it if truly novel tasks keep landing in the related band instead of escalating.

**Compose instead of sprawl** — if a skill is merely *related* (similarity in a band below the
routing threshold), `suggest_skills` returns it flagged `related: true` and the agent is told to
load and **extend or compose** it rather than author a near-duplicate. Any created skill is
immediately optimizable: the optimizer auto-drafts an eval task set if none exists.

---

## Keeping the optimizer honest (anti reward-hacking)

Optimizing a skill against an **LLM judge** invites the classic failure mode: the challenger learns
to please the judge, not to actually get better. Guards close the obvious paths:

1. **Judge ≠ author.** GEPA's reflection LM (`GEPA_MODEL`) writes the skill; the judge
   (`JUDGE_MODEL`) is a *different* model — same-model author/grader would share blind spots, so
   the optimizer warns loudly if you configure that. Set `JUDGE_MODELS=a,b` for an ensemble judge
   (mean score, majority-vote on failure dimensions) — harder still to exploit.
2. **Held-out gate, not a lucky mean.** Promotion requires a **margin** (`PROMOTE_MIN_MARGIN`,
   default +0.15, set above the judge's noise floor), **enough samples** (`PROMOTE_MIN_SAMPLES`),
   and **no catastrophic per-task regression** (the challenger may not drop a held-out task the
   champion passed below the pass line).
3. **No routing hacks.** If GEPA rewrites the routing `description`, promotion re-checks it against
   every other skill's — a rewrite that over-broadly **shadows** another skill (cosine ≥
   `COLLISION_SCORE`) is blocked, so a skill can't grab traffic by widening its trigger.
4. **Execution-grounded judging — sandboxed by default.** For code tasks an objective check
   (`execcheck.py`) extracts and `ast.parse`s the code and hands the judge a verdict it must treat
   as ground truth — "described the code" or a syntax error can't be talked into a high score.
   By default (`EXEC_SANDBOX=docker`) the code additionally *runs* in a **throwaway locked-down
   container**: no network, no mounts, read-only rootfs with tmpfs scratch, `nobody` user, all
   capabilities dropped, memory/pid/cpu limits. A missing-fixture error counts as inconclusive,
   not a defect — and if docker is unreachable the check **fails closed** to inconclusive; there
   is never a silent fallback to unsandboxed execution. `SANDBOX_RUNTIME=runsc` swaps in
   [gVisor](https://gvisor.dev)'s userspace kernel for true syscall isolation once installed;
   `EXEC_SANDBOX=1` is the legacy bare-subprocess mode (same user/filesystem/network — only for
   environments you'd let the judged code roam); `EXEC_SANDBOX=off` disables execution entirely.
   And a task can go all the way to **artifact-verified execution** by shipping a
   `check:` spec in its task YAML — the answer's code then runs in a scratch directory seeded by
   the fixture, and the verdict is whether the assertion holds on what it produced, not what a
   judge thinks of the prose:

   ```yaml
   - task: "Write a Python script that uppercases input.txt into output.txt."
     rubric: "Complete runnable code, reads input.txt, writes output.txt."
     check:
       fixture: |
         open("input.txt", "w").write("hello")
       assert: |
         assert open("output.txt").read() == "HELLO"
   ```

   A broken fixture or missing dependency counts as inconclusive — the harness's failure is never
   held against the answer. `check:` specs execute through the same sandbox (and are inconclusive
   when it's unavailable — they no longer run bare by default). The optimize services mount the
   docker socket for this: the *orchestrator* (trusted repo code) talks to the daemon, while the
   *judged code* runs confined in the sandbox container it launches — the judged code never sees
   the socket.
5. **Length penalty.** GEPA's objective subtracts a penalty for a bloated body, so it can't win by
   padding the skill with filler the judge mistakes for completeness.
6. **Deletions need evidence.** The reflection prompt tells GEPA not to remove guidance the observed
   failures don't implicate. If a challenger still drops most of the champion body (retention below
   `RETENTION_WARN`), the review UI shows a ⚠ warning with the retention number and the held-out
   sample count — a small eval can't quietly license a large deletion. (A warning, not a block: the
   tutorial's own rewrite is a legitimate wholesale fix, and the human reviews the diff either way.)
7. **Human override, informed.** A challenger that wins the mean but fails the gate is still
   recorded — the UI shows a red **⛔ promotion gate** banner with the reasons, so a human can
   override deliberately rather than rubber-stamp a gamed win.

```
[ab] champion 0.55 vs challenger 0.60 -> CHALLENGER WINS
[ab] ⛔ challenger won the mean but the promotion gate BLOCKED it:
     margin +0.10 < required +0.15; catastrophic regression on 1 task(s) the champion passed
```

## Configuration

Set in `.env` (never committed):

| var | default | notes |
|-----|---------|-------|
| `BASE_URL` | `https://openrouter.ai/api/v1` | endpoint for everything — any OpenAI-compatible provider; the `.env` template pins **Fireworks** (`https://api.fireworks.ai/inference/v1`). `OPENROUTER_BASE_URL` is the legacy alias |
| `API_KEY` | — | required — bearer token for `BASE_URL` ([Fireworks keys](https://fireworks.ai/account/api-keys)); `OPENROUTER_API_KEY` is the legacy alias. Local `http://` endpoints need no key |
| `AGENT_MODEL` | `qwen/qwen3.6-27b` | the agent — everything that *executes* skills, incl. GEPA rollouts; `MODEL` is the legacy alias. The `.env` template pins `accounts/fireworks/models/qwen3p7-plus` |
| `MODEL_BASE_URL` / `MODEL_API_KEY` | `BASE_URL` / `API_KEY` | serving-role-only overrides (agent runs, A/B agents, GEPA rollouts) for hybrid setups |
| `OPENROUTER_PROVIDERS` | — | OpenRouter only: optional provider allowlist (e.g. `fireworks,deepinfra` → `provider.only`) — composes with ZDR, trades pool resilience for vendor predictability; pin/model conflicts are caught at startup with the list of providers that do serve each model |
| `GEPA_MODEL` | `z-ai/glm-5.2` | GEPA's reflection LM (the skill author) |
| `STRONG_MODEL` | `GEPA_MODEL` | serves novel requests: when the router finds no skill at all, the agent runs on this model instead of `AGENT_MODEL` (weak/strong split at serving time), solves the task, and authors the new skill — so persisted skills are distilled from a strong solution. Uses the `BASE_URL` endpoint |
| `JUDGE_MODEL` | `google/gemini-2.5-flash` | the LLM judge — must differ from `GEPA_MODEL` (anti reward-hacking) |
| `MIN_SCORE` | `0.65` | at/above → routable match; below → `related` band or novel |
| `RELATED_SCORE` | `0.45` | floor of the `related` (compose/extend) band below `MIN_SCORE`; below it a task is *novel* (weak/strong escalation) |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | router embedding model — keep in sync with the Dockerfile's `EMBED_MODEL` build arg |
| `BODY_TARGET_CHARS` | `6000` | GEPA's length penalty starts past this body size |
| `LENGTH_PENALTY` | `0.10` | max score subtracted for a very long body |
| `LOOP_HEALTH_THRESHOLD` | `0.7` | continuous loop re-optimizes skills whose mined mean score is below this |
| `LOOP_PASSES` | `body` | passes the loop runs per unhealthy skill, in order (e.g. `body,description`) |
| `OPTIMIZE_STRATEGY` | `parallel` | inner-loop strategy: `parallel` = best-of-N + racing (concurrent, minutes), `gepa` = sequential reflective evolution — see [Optimization strategies](#optimization-strategies) |
| `OPTIMIZE_CANDIDATES` | `5` | parallel strategy: candidate rewrites authored and raced per run |
| `TAVILY_API_KEY` | — | optional author-side web research during the parallel pass — see [Optimization strategies](#optimization-strategies) |
| `GEPA_ROLLOUTS` | `direct` | rollout mode for either strategy: `direct` (one call under the serving contract) or `agent` (full scaffold per rollout — sees scaffold-driven failures, ~10× cost) |
| `RETENTION_WARN` | `0.5` | ⚠ review warning when the challenger keeps less than this fraction of the champion body |
| `OPTIMIZE_COMPONENTS` | `body` | what GEPA may rewrite; add `description` (routing gate applies) or `file:<path>` entries (diffed, never executed — avoid scripts) |
| `EXEC_SANDBOX` | `docker` | execution-grounded checks: `docker` = throwaway locked-down container (fails closed to inconclusive when docker is unreachable), `1` = bare subprocess (legacy), `off` = static checks only |
| `SANDBOX_IMAGE` | `ingot-optimize` | image the sandbox containers run — any image with this repo's code at `/app` |
| `SANDBOX_RUNTIME` | — | optional container runtime for sandbox runs, e.g. `runsc` for gVisor kernel-level isolation |
| `SKILL_MAX_DESCRIPTION` | `1024` | `create_skill` description hard cap (Agent Skills spec) |
| `SKILL_MAX_BODY` | `40000` | `create_skill` body ceiling (~500 lines) |
| `LANGFUSE_BASE_URL` | `http://langfuse-web:3000` (the bundled stack) | Langfuse API endpoint every service traces to and mines from — see [Using your own Langfuse project](#using-your-own-langfuse-project) |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | `pk-lf-local-demo` / `sk-lf-local-demo` | project API keys; the defaults are the bundled stack's headless-init literals (local demo values, not secrets) |
| `LANGFUSE_PUBLIC_URL` | `http://localhost:3100` | where your *browser* reaches Langfuse — the approval UI links traces here |

See [Keeping the optimizer honest](#keeping-the-optimizer-honest-anti-reward-hacking) for the
promotion-gate knobs (`PROMOTE_MIN_MARGIN`, `PROMOTE_MIN_SAMPLES`, `COLLISION_SCORE`, `JUDGE_MODELS`).

### Optimization strategies

The inner loop that turns a champion skill into a challenger has two strategies
(`OPTIMIZE_STRATEGY`); both feed the same held-out A/B and promotion gate — the honesty machinery
doesn't know or care which inner loop produced the challenger.

**`parallel` (default)** — best-of-N with racing (`optimize/bestofn.py`). Three concurrent waves:

1. **baseline** — the seed skill is rolled out on every train task at once; its judge feedback
   becomes the failure brief the authors write against
2. **author** — N candidate rewrites (`OPTIMIZE_CANDIDATES`, default 5) are drafted in parallel by
   the teacher model, each steered by a different angle (concise-imperative, worked-examples,
   edge-cases-first, …) so the pool isn't N copies of the same idea
3. **race** — successive halving over the train tasks: every survivor answers the next task (all
   rollouts and judge calls concurrent), the bottom half is dropped, repeat until the tasks run out

The finalists' cumulative mean — minus the same length penalty GEPA uses, so a candidate can't win
by bloating the body — picks the winner, and a winner that doesn't beat the seed returns the seed
unchanged. Wall-clock is bounded by the slowest single model call per wave: minutes, not tens of
minutes, on ~15 rollouts instead of GEPA's 60.

**`gepa`** (`--gepa`, or `OPTIMIZE_STRATEGY=gepa`) — the sequential reflective loop
(`optimize/gepa_loop.py`): propose → evaluate → reflect on observed failures → propose again,
under a `--budget` of metric calls (default 60). Slower and costlier, but each candidate is
*informed by the failures of earlier candidates* — worth it on mature skills where headroom is
small and blind parallel drafts plateau. (The trade in one line: `parallel` buys wall-clock with
breadth; `gepa` buys quality-per-rollout with depth.)

Independent of strategy, the champion's held-out A/B results are cached in `runs/eval-cache/`,
keyed by (skill revision, holdout tasks, serving model, judge). Most optimize runs end "champion
holds", so the next attempt against an unchanged champion only pays for the challenger's side of
the gate.

**Optional author-side web research** (`TAVILY_API_KEY`; `TAVILY_KEY` also accepted): when the
seed's failures look like knowledge gaps (correctness/completeness dimensions), the parallel pass
runs **one** web research step on the failing topics and hands every author the same brief —
flagged as potentially postdating the model's training and authoritative over its priors. Design
constraints, deliberately: research is **author-only** (the judge never sees it — rubrics stay the
fixed measuring stick), one shared brief per run (five authors independently searching would write
candidates against five different snapshots of the web — noise the race can't tell from quality),
briefs are cached content-addressed in `runs/research-cache/` (the autopilot re-optimizing a skill
costs zero extra searches), and formatting-only failures skip research entirely. Note the trust
boundary: searched content flows into a skill body that becomes an agent's system prompt — the
human review gate on every promotion is what stands between the web and your library.

### Writing eval task sets

Task sets are **runtime artifacts, not shipped opinions** — the repo commits none. They live in
`optimize/tasks/<skill>.yaml` (gitignored), and you get one per skill three ways: write it by hand,
let the teacher **auto-draft** one on a skill's first CLI optimize run, or promote the miner's
"weakest real tasks" candidates into it. Anatomy, annotated:

```yaml
skill: accelerated-computing-cudf
train:                # the optimizer sees these — rubrics are the GROUND TRUTH it distills
- task: You trained a large XGBoost model, but GPU inference is bottlenecked by Python
    overhead and row-by-row execution. Which RAPIDS feature can run the trained forest
    efficiently without retraining it?
  rubric: "Must name cuML's Forest Inference Library (FIL) — NOT Treelite (the exchange
    format FIL loads; models often answer Treelite, which is wrong). Must say FIL imports
    trained XGBoost, LightGBM, scikit-learn, and Treelite-format ensembles for batched GPU
    inference. Strong answers discuss batch size, tree layout, precision, memory, and when
    CPU inference still wins."
  deliverable: text   # optional: text | command | css | … — anything non-code disables the
                      # static "answer must contain a runnable Python block" check
holdout:              # the promotion gate ONLY trusts these — the optimizer never sees them
- task: Our fraud team has a LightGBM ensemble trained offline; scoring 200M rows nightly
    is too slow. Without retraining, how do we speed this up with RAPIDS, and what
    trade-offs should we plan for?
  rubric: "Must recommend FIL loading the LightGBM model … must discuss two trade-offs."
  deliverable: text
# optional per-task execution grounding (code tasks): the sandbox runs the answer's code
# against the fixture and asserts on its artifacts — an objective signal the judge can't
# be argued out of:
#   check:
#     fixture: open("input.txt", "w").write("hello")
#     assert: assert open("output.txt").read() == "HELLO"
routing:              # the description pass optimizes against these; the gate checks them
- task: "Which RAPIDS feature runs my trained forest on GPU without retraining?"
  expected: accelerated-computing-cudf
  harness: codex
- task: "Merge two PDF files and add page numbers."
  expected: null      # negatives: tasks that must NOT route here (no-route precision)
  harness: codex
```

The rules that make a set worth gating on: **holdout must be a real split** (a flat `tasks:` list
is flagged as leakage and can never promote), holdout tasks should *recombine* what train rubrics
teach rather than introduce new facts (the challenger can only learn what train carries — that's
also how skills for internal tools work: **your rubrics are how ground truth enters the system**,
the optimizer distills them into the body and the holdout proves it generalized), and every task
an entire pool aces is dead weight — an eval everything scores 1.0 on has zero power to rank
challengers.

### Using your own Langfuse project

By default `docker compose up` runs a **self-hosted Langfuse** for you (UI at
**http://localhost:3100**, login `demo@local.dev` / `localdemo123` — headless-init literals baked
into `docker-compose.yml`, not secrets; all demo traces land in its `ingot` project). To point
ingot at an **existing Langfuse project** instead — Langfuse Cloud or your own deployment — set
all three in `.env` and restart (`docker compose up -d`):

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...                  # your project's keys: Project Settings -> API Keys
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL (region URL for Cloud, e.g. https://us.cloud.langfuse.com)
LANGFUSE_PUBLIC_URL=https://cloud.langfuse.com # optional: where your browser reaches it (UI trace links)
```

Two gotchas:

- `LANGFUSE_BASE_URL` must be reachable **from inside the containers**. A Langfuse running
  elsewhere on the same machine is `http://host.docker.internal:<port>` (Docker Desktop) or your
  host's LAN IP — *not* `http://localhost:<port>`, which inside a container is the container itself.
- The bundled Langfuse stack still starts (it's harmless, just unused); it only no longer receives
  traces. Everything — agent tracing, `optimize-mine`, the canary loop — now reads and writes your
  project, so expect demo traffic to appear there.

The teacher/student split is deliberate: a strong model authors and judges skills, but rollouts and
the A/B always run on the model the skills will actually serve.

## How it works

- **`mcp_server/`** — [FastMCP](https://github.com/jlowin/fastmcp) v3 server (HTTP transport), six tools:
  - `suggest_skills(task, k)` — routable matches by embedding similarity (CPU [fastembed](https://github.com/qdrant/fastembed), no GPU); if none, returns near-misses flagged `related` (compose-awareness); empty = truly novel. (`list_skills()` exists for debug/UI but is kept out of the agent's toolset — the agent routes, it doesn't scan.)
  - `get_skill(name)` — the full SKILL.md to load; the header line carries the content-hash
    revision (`# Skill: <name>@<revision>`) for trace attribution
  - `create_skill(name, description, body)` — persist a new agent-authored skill (never overwrites)
  - `reload_skills()` — hot reload after promotion/creation (or `docker compose restart mcp`)
  - `route_and_load(task, harness, cwd, available_tools, available_mcps)` — optional one-round-trip
    selection for external clients; returns one compatible skill body or no match, plus a `novel`
    flag — the weak/strong escalation signal (see [Bring your own agent](#bring-your-own-agent-mcp-only))
- **`agent/run.py`** — [deepagents](https://github.com/langchain-ai/deepagents) LangGraph agent wired to those tools via `langchain-mcp-adapters`, traced to Langfuse (tagged with the routed skill and `revision=<name>@<rev>`). Serves routed tasks on the weak `AGENT_MODEL` and escalates truly novel tasks (empty `suggest_skills`) to `STRONG_MODEL`, which authors the new skill.
- **`skills/<name>/SKILL.md`** — YAML `description` is the routing key; the body is what the agent loads.
- **`optimize/`** — success/failure mining over real traces (`mine.py`), multi-dimensional LLM judge (`judge.py`), two inner-loop strategies — parallel best-of-N with racing (`bestofn.py`, the default) and the GEPA loop with diagnose→minimal-edit reflection (`gepa_loop.py`) — A/B + revisioned evidence (`ab.py`), live **canary** promotion (`canary.py`), snapshot/staged promotion with rollback (`promote.py`), per-role token ledger (`usage.py`). A/B agents get mutation tools stripped, so evals can't alter the library. Promotion records the exact skill revisions plus `evidence.json`/`EVIDENCE.md`, and refuses stale or mismatched revisions. The mining + categorized-failure ideas are borrowed from [SkillForge (Liu et al., arXiv:2604.08618)](https://arxiv.org/abs/2604.08618).
- **`ui/`** — FastAPI approval UI (one HTML page, no build step).

### Bring your own agent (MCP only)

Most deployments use just the MCP server with their own harness (Claude Code, Codex, a custom
agent) — the bundled `agent/run.py` is a reference client, not a requirement. Point your harness at
`http://localhost:8000/mcp` and call `route_and_load` once per request; its result is a three-way
branch:

- **`match`** — follow `skill_body`; a weak/cheap model suffices, the skill carries the method.
- **no match, `novel: false`** — related skills exist: call `suggest_skills` and compose or extend
  the closest instead of authoring a duplicate.
- **`novel: true`** — nothing even related. Serve the request with your strong model and have it
  persist its solution as a reusable skill via `create_skill` — the library grows exactly where
  routing failed, and the next similar request routes to the new skill on the weak model.

That three-way branch is the weak/strong serving split; the bundled agent implements the same
policy with `AGENT_MODEL` (weak) and `STRONG_MODEL` (strong, defaults to `GEPA_MODEL`). To keep the
trace-mining loop fed from your own harness, see
[Tracing from your own harness](#tracing-from-your-own-harness-mcp-only) at the end of this README.

### Optional shared skill roots

The Docker demo reads and writes `skills/`. To route across additional libraries, set
`SKILL_ROUTER_PATHS` to a platform-separated list of directories:

```bash
export SKILL_ROUTER_PATHS="$HOME/Source/team-skills:$HOME/.agents/skills"
docker compose up --build
```

The local `skills/` authoring root is searched first, followed by configured roots; the first
duplicate name wins with a warning. Optional `metadata.skill-router` frontmatter can restrict
automatic matches by harness, project path, platform, required tools/MCPs, trust, activation mode,
priority, and conflicts.

## Skill sources

**No skills are committed** — every source is optional and pulled from upstream by
`scripts/fetch_skills.sh` (clone → copy skill dirs → delete the clone), so each stays under its own
license and nothing is redistributed here. All are curated from the
[VoltAgent index](https://github.com/VoltAgent/awesome-agent-skills):

| source arg | repo | skills | license |
|------------|------|--------|---------|
| `anthropics` | [anthropics/skills](https://github.com/anthropics/skills) | document skills (pdf, docx, pptx, xlsx, …) | per-skill (see frontmatter) |
| `nvidia` | [nvidia/skills](https://github.com/nvidia/skills) | GPU / infra / data / medical imaging | Apache-2.0 |
| `lambdatest` | [LambdaTest/agent-skills](https://github.com/LambdaTest/agent-skills) | testing frameworks (pytest, playwright, cypress, appium, …) | MIT |
| `trailofbits` | [trailofbits/skills](https://github.com/trailofbits/skills) | security analysis (semgrep, static analysis, vuln scanners, …) | CC-BY-SA-4.0 |

```bash
scripts/fetch_skills.sh all                    # everything above (whole dirs, incl. bundled files)
scripts/fetch_skills.sh anthropics trailofbits # or pick sources
docker compose restart mcp                      # pick up the new skills
```

Fetching skips skills already present (never clobbers) and caps large sources. Trail of Bits' skills
are **CC-BY-SA-4.0** (share-alike); LambdaTest is **MIT**; nvidia is **Apache-2.0**; Anthropic's carry
per-skill licenses in their frontmatter — review each source's terms before redistributing.

## Security & threat model

**A loaded skill is instructions the agent follows.** That's the whole mechanism — so treat skill
content as *code*, and the skills library as *trusted state that must be curated*. You cannot fully
"solve" prompt injection in a system whose job is to retrieve and follow instructions; the design
goal is proportionate guardrails plus a small, well-defended write surface.

Write paths, and what guards each:

- **`create_skill` (agent-authored, goes live with no human approval)** — the highest-risk path, so
  it's the most guarded: slug + frontmatter sanitization (`yaml.safe_dump`), never overwrites an
  existing skill, Agent-Skills-spec name/description limits (≤64-char slug, ≤1024-char description,
  no reserved words, no XML tags), an instruction-override / prompt-injection phrase check
  (`mcp_server/safety.py`), an embedding **collision check** that rejects a description which
  near-duplicates an existing skill's (blocks *route-shadowing* / memory-poisoning), and an
  **optional ML classifier** (below). Accepted skills are tagged `source: agent` in frontmatter.
- **GEPA promotion** — content is authored by the reflection LM but **gated by human approval**: it
  lands in `runs/pending/` and you review the per-component diff in the UI before it goes live.
- **Third-party skills** (`skills/` from nvidia/anthropic) — unaudited but not attacker-controlled at
  runtime; review them as you would any dependency.

### Optional: ML prompt-injection classifier

Beyond the regex heuristic, `create_skill` can run the **[vLLM Semantic Router](https://github.com/vllm-project/semantic-router)
jailbreak detector** ([`llm-semantic-router/mmbert32k-jailbreak-detector-merged`](https://huggingface.co/llm-semantic-router/mmbert32k-jailbreak-detector-merged),
an mmBERT CPU classifier, Apache-2.0). Inference runs on **ONNX Runtime** via the model repo's
bundled ONNX export — no `torch`/`transformers`; the deps already ship with the base image via
fastembed. It's **opt-in**, and like the skills, the model is **not redistributed here** — it
downloads (~1.2GB, one-time) from Hugging Face into the HF cache on first use, under its own
upstream license. Just point the guard at the model:

```bash
# point the guard at the model (empty = disabled)
export SKILL_GUARD_MODEL=llm-semantic-router/mmbert32k-jailbreak-detector-merged
# optional: export SKILL_GUARD_THRESHOLD=0.7   (the classifier's default)
# optional: export SKILL_GUARD_ONNX_FILE=onnx/model.onnx   (which export to load)
```

With it set, every `create_skill` call is scored and a jailbreak/injection classification above the
threshold is rejected alongside the regex check (~20ms per call on CPU). When the model is missing
or the download fails it **degrades silently** to the regex heuristic — no crash. To run it in
Docker, set `SKILL_GUARD_MODEL` on the `mcp` service in `docker-compose.yml` (mount a persistent
`HF_HOME` to keep the one-time download).

### Network exposure

**Everything is localhost-only by default, because nothing is authenticated.** The MCP tools
(including the mutating `create_skill` / `reload_skills`) and the approval UI's endpoints (which can
trigger paid optimization runs and promote skills) have no auth of their own — the demo's protection
is that no service is reachable off the machine:

- `docker-compose.yml` publishes every port on loopback only (`127.0.0.1:8000` MCP,
  `127.0.0.1:8080` UI, `127.0.0.1:3100` Langfuse).
- Run directly (outside Docker), the MCP server also binds `127.0.0.1` by default; the compose file
  sets `HOST=0.0.0.0` *inside* the container, where it's still shielded by the loopback publish.

To make a service reachable from other machines on your network, change its port mapping in
`docker-compose.yml` from `"127.0.0.1:8000:8000"` to `"8000:8000"` (or bind a specific interface,
e.g. `"192.168.1.20:8000:8000"`) — same for the UI's `8080`. Do this knowingly: anyone who can reach
those ports can create skills, promote challengers, and start optimization runs that spend your
API budget. For anything beyond a trusted LAN, put an authenticating reverse proxy in front.

What is deliberately **not** done (and why): we do **not** denylist shell commands, `.env`/credential
mentions, or `curl … | sh` in skill bodies — legitimate skills routinely contain code, install steps,
and secret-handling guidance, so scanning for those produces constant false positives. The residual
risk is contained operationally instead: **run the agent in a container without real secrets or
sensitive host paths** (this demo's `agent` service mounts nothing sensitive and needs only
`API_KEY`). For a real deployment, add per-tool sandboxing and treat `create_skill` output
as untrusted until reviewed. Further reading:
[OpenAI on prompt injection](https://openai.com/safety/prompt-injections/).

## Tracing from your own harness (MCP only)

The optimizer's traffic signal (`optimize-mine`, the autopilot loop's health check) reads traces
from the self-hosted Langfuse over its public API — it does not care who wrote them. An MCP-only
deployment gets full mining parity by logging one trace per request that follows two conventions:

**1. A shape mine can parse** — either of:

- explicit: trace `input = {"task": "<user request>"}` (optional `"rubric"`), `output` = the final
  answer as a plain string;
- LangChain/LangGraph: attach the Langfuse `CallbackHandler` to your invocation — the logged
  `{"messages": [...]}` state on both sides is parsed as-is.

**2. Attribution tags** (optional, recommended) — tag the trace with the plain name of the skill
you served, plus `revision=<name>@<revision>` for exact-version attribution; tag `novel` when you
escalated to your strong model instead. Both `route_and_load` (`match` + `revision` fields) and
`get_skill` (header line `# Skill: <name>@<revision>`) hand you the identity. Mining counts a
tagged trace toward that skill directly; untagged traces fall back to embedding relevance (the
skill ranks in the top-5 for the task text — which still catches traffic a skill *should* have
served but didn't route).

A minimal sketch (Langfuse Python SDK v4 — the shape matters more than the SDK; on v3 the calls
differ slightly):

```python
from langfuse import get_client

lf = get_client()  # LANGFUSE_BASE_URL / _PUBLIC_KEY / _SECRET_KEY — same values as the compose stack
r = route_and_load(task, harness="claude", cwd=cwd)             # via MCP
tags = [r["match"], f"revision={r['match']}@{r['revision']}"] if r["match"] else ["novel"]
with lf.propagate_attributes(tags=tags):
    with lf.start_as_current_observation(name="serve", input={"task": task}) as span:
        answer = my_agent(task, r["skill_body"])                # your harness, your models
        span.update(output=answer)
```

With traces flowing, `docker compose run --rm optimize-mine <skill>` and the autopilot loop work
unchanged. Two caveats: mining re-judges traffic with `JUDGE_MODEL` (on your API bill), and the
optimizer's rollouts still execute on the bundled scaffold — set `AGENT_MODEL` to your production
serving model so what GEPA optimizes matches what you serve.
