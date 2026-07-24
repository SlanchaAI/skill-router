# Ingot × CARN Competitor Atlas

Date: 2026-07-23

## Scope

This atlas maps systems adjacent to Ingot's governed Agent Skills registry and
CARN's deterministic action replay. The generalized category is an
**evidence-gated capability cache**: route a request to an approved capability,
reuse a previously verified action graph only when its compatibility contract
still holds, and send divergences back through human-reviewed improvement.
[P, Ingot `ARCHITECTURE.md` and local CARN RFCs, 98]

The search covered 38 distinct candidates and deep-read 25. Repository and
paper performance claims remain author-reported unless reproduced here.
[P, primary repository and paper discovery, 88]

## Decision

Build the smallest vertical slice in this order:

1. **Body-aware, compatibility-first routing.** Retrieve over name,
   description, and bounded body text. Expose score components and abstain on
   ambiguity. [P, SkillRouter paper and `erichare/skill-route`, 95]
2. **Portable replay cassette.** Record typed actions and observations,
   content-address large payloads, replay offline, and stop at first
   divergence. [P, AgentReplay, Chidori, and Forkline source, 96]
3. **Verified replay admission.** A semantic match may nominate a cassette;
   exact workflow, tool/schema, policy, permission, and environment
   fingerprints plus node pre/postconditions decide whether it runs.
   [P, SkillDroid, AgentRR, and semantic-cache source, 91]
4. **Evidence-gated crystallization.** Repeated clean runs may propose a
   capability revision; any failure, drift, or override demotes it. Ingot's
   existing quarantine and human promotion remain the only activation path.
   [P, Progressive Crystallization and Ingot architecture, 91]
5. **Empirical capability graph.** CARN traces propose dependency,
   complement, alternative, and lineage edges. Reviewed edges may rerank
   candidates under a strict context budget. [P, Graph of Skills, SkillOps,
   and local decomposer experiment, 92]

Do not turn Ingot into a workflow engine. Ingot owns identity, routing,
evidence, promotion, rollback, and audit. CARN owns execution recording,
replay, divergence, and trace-to-program compilation. `route_and_load`
remains Ingot's sole serving-selection contract. [P, Ingot architecture and
local CARN RFCs, 98]

## Non-negotiable invariants

- Compatibility filtering precedes ranking. [P, Ingot architecture, 99]
- At most one skill body crosses the routing boundary. [P, Ingot
  architecture, 99]
- Fuzzy similarity proposes; it never authorizes side effects. [P, Agentic
  Plan Caching accuracy trade-off and semantic-cache implementations, 93]
- Replay fails closed on a missing or mismatched fingerprint, action,
  observation, precondition, or postcondition. [P, CARN RFC-0003, Chidori,
  AgentRR, and SkillDroid, 96]
- Pending learned artifacts remain inert until evidence and human approval
  promote their content-addressed revision. [P, Ingot architecture, 99]
- Unlicensed and AGPL-3.0 implementations are idea-only inputs. No source is
  copied into Ingot. [P, repository license files and root-tree audits, 99]

## Market map

### Skill routing and retrieval

**SkillRouter** embeds `name | description | full body`, retrieves a broad
candidate set, then reranks a smaller set. Its 80K-skill evaluation reports
74.0% Hit@1, and its ablation attributes a 29–44 point loss to removing the
body. This is the strongest direct evidence that Ingot's description-only
embedding is under-specified. Code license: MIT; model and data retain separate
upstream terms. [P, [repository](https://github.com/zhengyanzhao1997/SkillRouter)
and [paper](https://arxiv.org/abs/2603.22455), 96]

**SkillFlow** uses a four-stage 36K→1000→100→10→5 funnel over full skill
content. It demonstrates the scale shape but its final model filter is too
heavy for Ingot's default local serving path. License: Apache-2.0.
[P, [repository](https://github.com/IBPA/skill-flow), 92]

**skill-route** combines lexical, semantic, repository-context, and graph
scores, then clarifies when confidence is low or the top two candidates are
close. Its score decomposition and relation vocabulary are useful; its static
weights are not evidence of universal thresholds. License: MIT.
[P, [repository](https://github.com/erichare/skill-route), 96]

**Graph of Skills** seeds with semantic and lexical retrieval, expands through
dependency/workflow/semantic/alternative edges, applies personalized PageRank,
and hydrates a bounded bundle. Take the graph-rerank shape after CARN supplies
empirical edges; do not hand-author a speculative graph first. License: MIT.
[P, [repository](https://github.com/davidliuk/graph-of-skills) and
[paper](https://arxiv.org/abs/2604.05333), 95]

### Skill hierarchy, governance, and evolution

**jscraik/Agent-Skills** separates canonical source, hashed manifests, and
context-budgeted runtime projections. It also models typed graph relations,
evidence accumulation, and signed promotion. Several mechanisms are design
contracts in a small project, but the source→projection boundary fits Ingot.
License: Apache-2.0. [P,
[repository](https://github.com/jscraik/Agent-Skills), 96]

**Memento-Skills** implements read→execute→reflect→write with semantic
dispatch, utility updates, rewrites, creation, and a market. It is the closest
product competitor, but its repository has no root software license. Take only
the phase separation; route every write into Ingot quarantine.
[P, [repository](https://github.com/Memento-Teams/Memento-Skills), 97]

**SkillOps** represents skills as precondition, operation, artifact, validator,
and failure modes, with dependency, compatibility, redundancy, alternative,
and lineage edges. Its split between task-time repair and library-time
maintenance is the cleanest shared contract for Ingot and CARN. License: MIT.
[P, [repository](https://github.com/Hik289/SkillOps) and
[paper](https://arxiv.org/abs/2605.13716), 94]

**AgentSkillOS** proposes a recursive capability tree with active and dormant
layers plus a skill Directed Acyclic Graph (DAG). The repository has no root
license despite an MIT badge, so it is an idea-only reference.
[P, [repository](https://github.com/ynulihao/AgentSkillOS) and
[paper](https://arxiv.org/abs/2603.02176), 94]

**Fractal** manages bounded trees of agent loops in isolated Git worktrees with
lineage, inherited configuration, budgets, lifecycle, SQLite state, and
operator signals. This informs execution-tree operations, not skill hierarchy.
License: Apache-2.0. [P,
[repository](https://github.com/plasma-ai/fractal), 96]

**SkillHub** provides immutable semantic versions, beta/stable/latest channels,
namespaces, layered review, comparison, and audit. Ingot already has the
stronger content hash and evidence gate; named channels and namespace
promotion are later distribution features. License: Apache-2.0.
[P, [repository](https://github.com/iflytek/skillhub), 97]

**agentregistry** reconciles a requested mutable Git reference to an observed
immutable commit and records controller status. That requested→observed model
is useful for external skill sources. License: Apache-2.0.
[P, [repository](https://github.com/agentregistry-dev/agentregistry), 96]

### Recording, replay, and divergence

**Chidori** records deterministic host results for prompt, tool, and HTTP calls
in sequence, then replays without model calls. Resume and approvals work by
replaying to a suspension point. Take the small host-boundary contract and
strict sequence matching. License: Apache-2.0.
[P, [repository](https://github.com/ThousandBirdsInc/chidori), 96]

**AgentReplay** stores a JSON cassette, JSONL events, content-addressed blobs,
and an optional SQLite index. LIVE, RECORD, REPLAY, and HYBRID modes plus
counterfactual forks make it the best portable regression format. It cannot
isolate unwrapped side effects, so replay must pair with a deny-network
sandbox or typed side-effect adapter. License: MIT.
[P, [repository](https://github.com/gadda00/agentreplay), 97]

**Forkline** supplies append-only SQLite events, offline network blocking,
deterministic normalization, first-divergence diffs, and stable Continuous
Integration (CI) exit codes. Take the operator-facing comparison semantics,
not its whole run store. License: Apache-2.0.
[P, [repository](https://github.com/sauravvenkat/forkline), 95]

**SkillDroid** compiles successful mobile trajectories into parameterized
steps with typed slots, weighted locators, state fingerprints, postcondition
skips, bounded repair, fallback, and failure-conditioned variants. It is the
strongest replay architecture, but only a paper and mobile evaluation are
available. [P, [paper](https://arxiv.org/abs/2604.14872), 90]

**AgentRR** treats validators as first-class replay artifacts, checking flow
integrity, preconditions, parameter constraints, and safety invariants. It
supports storing literal experience beside abstract procedure, but publishes
no reusable implementation. [P,
[paper](https://arxiv.org/abs/2505.17716), 82]

**Progressive Crystallization** promotes recurring behavior through agentic,
hybrid, and deterministic tiers, then circuit-breaks back on drift or
regression. Its reported thresholds are product-specific, not defaults for
Ingot, but the promote/demote lifecycle is directly useful.
[P, [paper](https://arxiv.org/abs/2607.07052), 85]

**ActiveGraph** treats an append-only event log as truth and every graph or
trace as a deterministic projection. Forks reference an inclusive immutable
event prefix; promotion applies the structural delta and refuses stale-parent
conflicts. Take event-prefix lineage and typed structural diff. License:
Apache-2.0. [P, [repository](https://github.com/yoheinakajima/activegraph),
96]

**Temporal** re-executes workflow code while requiring generated commands to
match the ordered event history. Its recommended deployment check replays
representative histories against candidate code and fails on nondeterminism.
Take the release-gate contract, not the service. License: MIT.
[P, [official documentation](https://docs.temporal.io/workflow-execution),
97]

**DBOS** restarts deterministic workflow functions and returns checkpointed
step outputs until the first missing step. Step identity/order and application
version are pinned; forks copy a verified prefix into a new run. Take
copy-on-fork checkpoints and explicit candidate-version selection. License:
MIT. [P, [official documentation](https://docs.dbos.dev/architecture), 96]

These systems sharpen the stable Ingot/CARN seam:
`record(run) → bundle`, `verify(bundle, candidate) → verdict`,
`fork(bundle, anchor, patches) → child`, `diff(parent, child) → typed delta`,
then `gate(verdict, delta, policy) → pass | block | review`.
[S, durable-workflow synthesis, 96]

### Caching, tries, and insertion

**Agentic Plan Caching** is the direct baseline: cache a parameterized plan
after a correct run, retrieve by exact intent or optional semantic similarity,
and adapt it with a lightweight planner. Its experiments show a lower fuzzy
threshold increases hits and lowers cost while reducing accuracy. Ingot × CARN
must therefore beat it on validated reuse, not raw hit rate.
[P, [paper](https://arxiv.org/abs/2506.14852), 92]

**Probabilistic Language Tries** frame action prefixes as a policy-weighted
trie: retain high-value prefixes and recompute novel residuals. Use a DAG/trie
for shared action spines, but validate each branch against current state.
[P, [paper](https://arxiv.org/abs/2604.06228), 84]

**SGLang** and **LMCache** show exact-prefix retention, longest-prefix
scheduling, reference-counted eviction, and selective residual recomputation.
They are storage analogies, not semantic workflow competitors. Both are
Apache-2.0. [P, [SGLang](https://github.com/sgl-project/sglang) and
[LMCache](https://github.com/LMCache/LMCache), 95]

**Portkey**, **LangChain Redis**, and **GPTCache** show low-friction gateway or
framework insertion. They also show why action replay needs more identity than
prompt similarity: model configuration, tool and policy schemas, permissions,
environment state, and postconditions must participate in validity.
[P, [Portkey](https://github.com/Portkey-AI/gateway),
[LangChain Redis](https://github.com/langchain-ai/langchain-redis), and
[GPTCache](https://github.com/zilliztech/GPTCache), 94]

## Clean-room take ledger

| Mechanism | Source | License posture | Ingot/CARN implementation seam |
|---|---|---|---|
| Full-body candidate representation | SkillRouter | MIT code; model/data separate | `mcp_server/router.py` |
| Hybrid retrieval + score explanation | skill-route | MIT | Router scoring record |
| Graph expansion under a body budget | Graph of Skills | MIT | Later empirical reranker |
| Typed capability contract | SkillOps | MIT | Skill metadata + replay manifest |
| Canonical source→projection | Agent-Skills | Apache-2.0 | Registry load representation |
| Strict host-call cassette | Chidori | Apache-2.0 | New replay module |
| JSONL + content-addressed blobs | AgentReplay | MIT | New replay store |
| First-divergence/offline CI | Forkline | Apache-2.0 | Replay diagnostics and CLI |
| Typed slots + node validators | SkillDroid/AgentRR | Paper only | Clean-room manifest design |
| Promote/demote lifecycle | Progressive Crystallization | Paper only | Existing evidence gate |
| Shared-prefix DAG/trie | PLT/SGLang | Paper/Apache-2.0 | Later replay compaction |
| Gateway insertion | Portkey/LangChain | MIT | MCP and agent adapter |
| Trace-to-process mining | PM4Py | AGPL-3.0 | Service boundary or independent code only |
| Self-evolving write-back | Memento | Unlicensed | Ideas only; no source copy |

## White space and moat

The code-level category is crowded. A body-aware router, cassette recorder, or
workflow compiler can be rebuilt quickly. Defensibility must come from a
permissioned evidence network: canonical task classes, exact environment
manifests, accepted action graphs, validators, failures, overrides,
regressions, and promotion outcomes tied to immutable revisions.
[P, competitor comparison, 91]

The initial buyer is an enterprise agent-platform or automation team already
running recurring, expensive, side-effectful tasks. The first paid transaction
is a private capability registry and replay release gate for one production
agent fleet. The compounding asset exists only if contracts grant durable
rights to retain and aggregate de-identified compatibility and outcome
evidence; customer-isolated installs without those rights produce software
revenue but no cross-customer data moat. [S, market inference from competitor
mechanisms, 72]

Positioning: **Ingot is the compatibility and reliability registry for
autonomous work.** CARN turns traces into proposed executable capabilities;
Ingot proves which revision is safe in which environment and controls
activation. [S, synthesis, 86]

## Kill conditions

- Full-body routing does not improve held-out top-1 or recall at scale over the
  current description-only baseline. [S, falsification criterion, 90]
- Validated replay cannot reduce model/tool work without matching frontier
  success and maintaining zero silent wrong replays. [S, falsification
  criterion, 95]
- Each integration requires bespoke wrappers instead of one MCP/framework
  insertion seam. [S, adoption criterion, 86]
- Buyers will not grant rights needed to aggregate compatibility and outcome
  evidence. [S, moat criterion, 88]
- Onboarding and operating cost exceed saved inference and labor. [S,
  economics criterion, 90]

## Follow-through tracker

| Finding | Owner layer | Status | Proof required |
|---|---|---|---|
| Full-body routing | Ingot | BUILDING | Held-out baseline vs challenger |
| Explainable abstention | Ingot | PLANNED | Ambiguity and no-route tests |
| Portable strict cassette | CARN seam | PLANNED | Offline replay + divergence test |
| Compatibility manifest | Shared contract | PLANNED | Adversarial mismatch rejection |
| Evidence-gated replay promotion | Ingot | PLANNED | Pending artifact cannot serve |
| Empirical graph rerank | CARN→Ingot | DEFERRED | Trace-derived edge lift |
| Shared-prefix DAG | CARN | DEFERRED | Storage/latency win without accuracy loss |
| Named registry channels | Ingot | DEFERRED | Buyer demand |

Mapped 38 findings. Zero were shipped when this atlas was written; the tracker,
commits, and measured caller evidence are the result.
