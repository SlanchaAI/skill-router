# Skill decomposer and matcher candidates

Corpus: `/corpus`

Parsed 48 skills, 392 sections, 182 cross-skill matches, and 14 clusters.

Candidate clusters are bounded three-skill similarity triangles. They are retrieval leads, not proof that a shared workflow exists.

## Candidate clusters

### Cluster 1: 3 skills, mean matched cosine 0.832

- **essay-cuts: essay-cuts > 5. Schedule (Zernio) + verify** (`essay-cuts/SKILL.md:75`): `Z=~/Source/dotfiles-claude/skills/social-media-assistant/scripts/zernio.py` - **X**: ONE self-contained post (`x1`) — hook → payoff → canonical link; long-form allowed (Premium/verified, no 280 cap), but front-load the hook (only ~280 show
- **posting-to-socials: posting-to-socials > Tooling (optional)** (`posting-to-socials/SKILL.md:113`): - **Scheduling across connected accounts, headless:** `social-media-assistant` skill wraps the Zernio API for LinkedIn/X/Reddit/Discord. Use it when firing many posts on a schedule matters more than hand-placing each one. Note its constrain
- **social-media-assistant: social-media-assistant > Sequencing (mirrors DISTRIBUTION.md, adapted for scheduling)** (`social-media-assistant/SKILL.md:68`): Given canonical publish time T (e.g. Mon 08:00 PT): - **T**: Substack (scheduled in Substack itself - title A/B experiment + subscribe buttons live there). - **T+2h**: X/Twitter (Zernio). - **T+3h**: LinkedIn (Zernio). - **T+3-5h, or next d

### Cluster 2: 3 skills, mean matched cosine 0.823

- **essay-cuts: essay-cuts > 5. Schedule (Zernio) + verify** (`essay-cuts/SKILL.md:75`): `Z=~/Source/dotfiles-claude/skills/social-media-assistant/scripts/zernio.py` - **X**: ONE self-contained post (`x1`) — hook → payoff → canonical link; long-form allowed (Premium/verified, no 280 cap), but front-load the hook (only ~280 show
- **posting-to-socials: posting-to-socials > Tooling (optional)** (`posting-to-socials/SKILL.md:113`): - **Scheduling across connected accounts, headless:** `social-media-assistant` skill wraps the Zernio API for LinkedIn/X/Reddit/Discord. Use it when firing many posts on a schedule matters more than hand-placing each one. Note its constrain
- **social-media-assistant: social-media-assistant > Zernio client** (`social-media-assistant/SKILL.md:36`): `scripts/zernio.py` - self-contained, stdlib-only. Key + account IDs from 1Password **Slancha** vault (`op://Slancha/slancha-zernio`), read via the `slancha-op` service-account wrapper (headless, no biometric). API base `https://api.zernio.

### Cluster 3: 3 skills, mean matched cosine 0.818

- **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** (`build-vs-buy/SKILL.md:44`): Compose **monument** (landscape) or **deep-crawl** (a few named candidates) — primary-source, **license-verified from the raw LICENSE** (flag AGPL/commercial traps), currency-checked (is it maintained *now*?), and self-host/lock-in assessed
- **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** (`deep-crawl/SKILL.md:78`): Per target, produce: - **pages_read** (count — the honesty anchor). - **what_it_is** — the real technical core, in your words, after reading. - **full_feature_inventory** — EVERY distinct capability found (not a top-5). - **architecture** —
- **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)** (`monument/SKILL.md:256`): - **Work budget:** Phase 1 ~50–80 discovery passes + top-ups; Phase 3 ~600–800 stages. Triple digits, legitimately — driven by coverage (until dry) + per-entry deep-crawl, never padding. - **No nothing-burgers:** every atlas claim traces to

### Cluster 4: 3 skills, mean matched cosine 0.816

- **build-vs-buy: (untitled) > The method > 3 — Score on the axes that actually decide buy-over-build** (`build-vs-buy/SKILL.md:56`): Not a feature checklist — these: - **Maintenance eliminated** — what on-call / upkeep / dependency-churn does buying remove? - **Focus reclaimed** — engineer-time returned to the actual business (the real point). - **Feature velocity** — do
- **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** (`deep-crawl/SKILL.md:78`): Per target, produce: - **pages_read** (count — the honesty anchor). - **what_it_is** — the real technical core, in your words, after reading. - **full_feature_inventory** — EVERY distinct capability found (not a top-5). - **architecture** —
- **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)** (`monument/SKILL.md:256`): - **Work budget:** Phase 1 ~50–80 discovery passes + top-ups; Phase 3 ~600–800 stages. Triple digits, legitimately — driven by coverage (until dry) + per-entry deep-crawl, never padding. - **No nothing-burgers:** every atlas claim traces to

### Cluster 5: 3 skills, mean matched cosine 0.816

- **monument: (untitled) > The pipeline (five phases) > Phase 5 — Implementation ledger + follow-through (the monument is not done here)** (`monument/SKILL.md:227`): The atlas is a map, not a result. A monument that ends at Phase 4 reliably **rots**: the findings get built (or not), never wired into a live path, never measured — and the next monument re-discovers what the last one already decided and ne
- **monument-followthrough: (untitled) > When to use** (`monument-followthrough/SKILL.md:39`): - Right after a `monument` / `build-monument` / `research-spec` deliverable, as the closing gate (the monument is NOT done when the atlas ships — it's done when the high-rank findings are shipped-and-measured or explicitly deferred/killed).
- **search-council: search-council > When to use** (`search-council/SKILL.md:26`): - **monument** Phase 1 (discovery) — the web sweep that must be web-sourced, never memory-sourced. - **sota-check** — the current-state pulse. - Any "find as many real repos/products/papers on topic X as exist" request where completeness ma

### Cluster 6: 3 skills, mean matched cosine 0.815

- **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** (`deep-crawl/SKILL.md:78`): Per target, produce: - **pages_read** (count — the honesty anchor). - **what_it_is** — the real technical core, in your words, after reading. - **full_feature_inventory** — EVERY distinct capability found (not a top-5). - **architecture** —
- **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)** (`monument/SKILL.md:256`): - **Work budget:** Phase 1 ~50–80 discovery passes + top-ups; Phase 3 ~600–800 stages. Triple digits, legitimately — driven by coverage (until dry) + per-entry deep-crawl, never padding. - **No nothing-burgers:** every atlas claim traces to
- **monument-followthrough: (untitled) > The method > 1. Classify each finding through the 5 stages — trace, don't grep-and-assume** (`monument-followthrough/SKILL.md:63`): For each finding, determine the **furthest stage it has truly reached**. The verdicts: | Verdict | Meaning | |---|---| | `SHIPPED` | wired + measured-positive + on default/prod. Done. | | `MEASURED+` | measured better than baseline but not

### Cluster 7: 3 skills, mean matched cosine 0.812

- **deep-crawl: (untitled) > Scaling** (`deep-crawl/SKILL.md:116`): **One site:** enumerate inline, split the page list into batches of at most 15 URLs, and use parallel readers only when available. Keep one dossier writer; readers return evidence and never write competing dossier files. **A landscape sweep
- **monument: (untitled) > The pipeline (five phases) > Phase 3 — Deep-crawl EVERYTHING selected (compose the `deep-crawl` skill)** (`monument/SKILL.md:169`): Run the **`deep-crawl`** skill on every selected entry: enumerate every page (llms.txt → sitemap → docs nav → footer → GitHub tree), read it all, produce a dossier (full feature/finding inventory + architecture + verified license/pricing +
- **search-council: search-council > Composing it** (`search-council/SKILL.md:124`): - **monument** Phase 1: replace the single-agent web sweep with a search-council fan-out; feed `entries` into the atlas, `blind_spots` into white-space. (One-line edit, lands after the gate.) - **sota-check** step 2/3: fan the current-state

### Cluster 8: 3 skills, mean matched cosine 0.807

- **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** (`build-vs-buy/SKILL.md:44`): Compose **monument** (landscape) or **deep-crawl** (a few named candidates) — primary-source, **license-verified from the raw LICENSE** (flag AGPL/commercial traps), currency-checked (is it maintained *now*?), and self-host/lock-in assessed
- **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** (`deep-crawl/SKILL.md:78`): Per target, produce: - **pages_read** (count — the honesty anchor). - **what_it_is** — the real technical core, in your words, after reading. - **full_feature_inventory** — EVERY distinct capability found (not a top-5). - **architecture** —
- **monument: (untitled) > The pipeline (five phases) > Phase 3 — Deep-crawl EVERYTHING selected (compose the `deep-crawl` skill)** (`monument/SKILL.md:169`): Run the **`deep-crawl`** skill on every selected entry: enumerate every page (llms.txt → sitemap → docs nav → footer → GitHub tree), read it all, produce a dossier (full feature/finding inventory + architecture + verified license/pricing +

### Cluster 9: 3 skills, mean matched cosine 0.807

- **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** (`build-vs-buy/SKILL.md:44`): Compose **monument** (landscape) or **deep-crawl** (a few named candidates) — primary-source, **license-verified from the raw LICENSE** (flag AGPL/commercial traps), currency-checked (is it maintained *now*?), and self-host/lock-in assessed
- **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** (`deep-crawl/SKILL.md:78`): Per target, produce: - **pages_read** (count — the honesty anchor). - **what_it_is** — the real technical core, in your words, after reading. - **full_feature_inventory** — EVERY distinct capability found (not a top-5). - **architecture** —
- **monument: (untitled) > The pipeline (five phases) > Phase 4 — Synthesize + persona-review gate #2 (the atlas)** (`monument/SKILL.md:190`): Cluster the dossiers into a **landscape atlas**: - **By axis** (the fronts) → who owns what, where it's crowded, where it's empty. - **By relation:** `complement` (integrate), `competitor` (beat/differentiate), `substrate` (build on), `anal

### Cluster 10: 3 skills, mean matched cosine 0.806

- **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** (`build-vs-buy/SKILL.md:44`): Compose **monument** (landscape) or **deep-crawl** (a few named candidates) — primary-source, **license-verified from the raw LICENSE** (flag AGPL/commercial traps), currency-checked (is it maintained *now*?), and self-host/lock-in assessed
- **deep-crawl: (untitled) > Hunt the surprises (the load-bearing section)** (`deep-crawl/SKILL.md:90`): A skim is dangerous because it's confidently wrong. Actively check for: - **Pivots / stale positioning** — does the product still do what the homepage hero says? (A "data-security" company that's now a memory product; a "browser agent" that
- **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)** (`monument/SKILL.md:256`): - **Work budget:** Phase 1 ~50–80 discovery passes + top-ups; Phase 3 ~600–800 stages. Triple digits, legitimately — driven by coverage (until dry) + per-entry deep-crawl, never padding. - **No nothing-burgers:** every atlas claim traces to

### Cluster 11: 3 skills, mean matched cosine 0.804

- **launching: launching > The sequence (compress or stretch, keep the order)** (`launching/SKILL.md:17`): | T-day | Action | |---|---| | T-3 → T-1 | Prep: assets, drafts, fresh-clone/install test, PH teaser page + account engagement, warm-up thread participation (practitioner voice, zero launch links) | | T-1 | Influencers (free-mention ask) +
- **posting-to-socials: posting-to-socials > Cross-platform mechanics** (`posting-to-socials/SKILL.md:85`): - **Canonical-first ordering.** If posts point to a canonical page (blog/repo/landing), that page must be **live and resolving before** any channel post links to it. A scheduled or not-yet-published URL 404s in front of readers — the one un
- **social-media-assistant: social-media-assistant > Sequencing (mirrors DISTRIBUTION.md, adapted for scheduling)** (`social-media-assistant/SKILL.md:68`): Given canonical publish time T (e.g. Mon 08:00 PT): - **T**: Substack (scheduled in Substack itself - title A/B experiment + subscribe buttons live there). - **T+2h**: X/Twitter (Zernio). - **T+3h**: LinkedIn (Zernio). - **T+3-5h, or next d

### Cluster 12: 3 skills, mean matched cosine 0.804

- **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** (`deep-crawl/SKILL.md:78`): Per target, produce: - **pages_read** (count — the honesty anchor). - **what_it_is** — the real technical core, in your words, after reading. - **full_feature_inventory** — EVERY distinct capability found (not a top-5). - **architecture** —
- **monument: (untitled) > The pipeline (five phases) > Phase 4 — Synthesize + persona-review gate #2 (the atlas)** (`monument/SKILL.md:190`): Cluster the dossiers into a **landscape atlas**: - **By axis** (the fronts) → who owns what, where it's crowded, where it's empty. - **By relation:** `complement` (integrate), `competitor` (beat/differentiate), `substrate` (build on), `anal
- **monument-followthrough: (untitled) > The method > 1. Classify each finding through the 5 stages — trace, don't grep-and-assume** (`monument-followthrough/SKILL.md:63`): For each finding, determine the **furthest stage it has truly reached**. The verdicts: | Verdict | Meaning | |---|---| | `SHIPPED` | wired + measured-positive + on default/prod. Done. | | `MEASURED+` | measured better than baseline but not

### Cluster 13: 3 skills, mean matched cosine 0.796

- **build-vs-buy: (untitled) > The method > 3 — Score on the axes that actually decide buy-over-build** (`build-vs-buy/SKILL.md:56`): Not a feature checklist — these: - **Maintenance eliminated** — what on-call / upkeep / dependency-churn does buying remove? - **Focus reclaimed** — engineer-time returned to the actual business (the real point). - **Feature velocity** — do
- **deep-crawl: (untitled) > Hunt the surprises (the load-bearing section)** (`deep-crawl/SKILL.md:90`): A skim is dangerous because it's confidently wrong. Actively check for: - **Pivots / stale positioning** — does the product still do what the homepage hero says? (A "data-security" company that's now a memory product; a "browser agent" that
- **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)** (`monument/SKILL.md:256`): - **Work budget:** Phase 1 ~50–80 discovery passes + top-ups; Phase 3 ~600–800 stages. Triple digits, legitimately — driven by coverage (until dry) + per-entry deep-crawl, never padding. - **No nothing-burgers:** every atlas claim traces to

### Cluster 14: 3 skills, mean matched cosine 0.796

- **deep-crawl: (untitled) > Scaling** (`deep-crawl/SKILL.md:116`): **One site:** enumerate inline, split the page list into batches of at most 15 URLs, and use parallel readers only when available. Keep one dossier writer; readers return evidence and never write competing dossier files. **A landscape sweep
- **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)** (`monument/SKILL.md:256`): - **Work budget:** Phase 1 ~50–80 discovery passes + top-ups; Phase 3 ~600–800 stages. Triple digits, legitimately — driven by coverage (until dry) + per-entry deep-crawl, never padding. - **No nothing-burgers:** every atlas claim traces to
- **search-council: search-council > Composing it** (`search-council/SKILL.md:124`): - **monument** Phase 1: replace the single-agent web sweep with a search-council fan-out; feed `entries` into the atlas, `blind_spots` into white-space. (One-line edit, lands after the gate.) - **sota-check** step 2/3: fan the current-state

## Strongest section pairs

- `0.915` **launching: launching > Channel rules (the expensive lessons)** ↔ **posting-to-socials: posting-to-socials > Reddit**
- `0.891` **barkeep: barkeep — route spendy work onto idle pools; run other CLIs as workers > The decorrelated-reviewer seam (build-loop)** ↔ **build-loop: Build loop > Cross-provider runner**
- `0.881` **deep-crawl: (untitled) > Routing** ↔ **monument: (untitled) > Routing**
- `0.864` **posting-to-socials: posting-to-socials > Tooling (optional)** ↔ **social-media-assistant: social-media-assistant > Zernio client**
- `0.861` **game-dev: game-dev — build a game that plays well and can be balanced > When NOT to use** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > When NOT to use**
- `0.857` **posting-to-socials: posting-to-socials > Tooling (optional)** ↔ **social-media-assistant: social-media-assistant > Two rails: Zernio (API) vs Playwright (browser)**
- `0.854` **essay-cuts: essay-cuts > 5. Schedule (Zernio) + verify** ↔ **social-media-assistant: social-media-assistant > Sequencing (mirrors DISTRIBUTION.md, adapted for scheduling)**
- `0.852` **monument: (untitled) > The pipeline (five phases) > Phase 5 — Implementation ledger + follow-through (the monument is not done here)** ↔ **monument-followthrough: (untitled) > When to use**
- `0.852` **deep-crawl: (untitled) > Scaling** ↔ **monument: (untitled) > The pipeline (five phases) > Phase 3 — Deep-crawl EVERYTHING selected (compose the `deep-crawl` skill)**
- `0.851` **memory-defrag: Memory Defrag > Guidelines** ↔ **memory-reflect: Memory Reflect > Guidelines**
- `0.849` **game-dev: game-dev — build a game that plays well and can be balanced > When NOT to use** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > When to use**
- `0.848` **game-dev: game-dev — build a game that plays well and can be balanced > Composes with** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > Composes with**
- `0.846` **assumption-audit: (untitled) > Foundry at scale** ↔ **build-vs-buy: (untitled) > Foundry at scale**
- `0.845` **posting-to-socials: posting-to-socials > Tooling (optional)** ↔ **social-media-assistant: social-media-assistant > Sequencing (mirrors DISTRIBUTION.md, adapted for scheduling)**
- `0.844` **memory-defrag: Memory Defrag > When to Run** ↔ **memory-reflect: Memory Reflect > When to Run**
- `0.844` **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** ↔ **monument: (untitled) > The pipeline (five phases) > Phase 3 — Deep-crawl EVERYTHING selected (compose the `deep-crawl` skill)**
- `0.844` **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** ↔ **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)**
- `0.842` **game-dev: game-dev — build a game that plays well and can be balanced > Architecture defaults (adopt lightly, don't over-impose)** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > The 7 dimensions**
- `0.841` **ltx-farm: ltx-farm — drive the local LTX-2.3 render farm > Storyboard gate + finishing (2026-07-16, slancha-studio)** ↔ **video-gen: video-gen — generate, judge, and treat motion footage > The Dell LTX stack (`~/ltx/`)**
- `0.836` **overnight-studio: Overnight studio — brief → generate → judge → assemble, unattended** ↔ **video-gen: video-gen — generate, judge, and treat motion footage > Studio-scale addenda (overnight run, 2026-07-05 — 490 clips, 25 films)**
- `0.835` **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier** ↔ **monument: (untitled) > The pipeline (five phases) > Phase 4 — Synthesize + persona-review gate #2 (the atlas)**
- `0.834` **game-dev: game-dev — build a game that plays well and can be balanced > When NOT to use** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > Composes with**
- `0.832` **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** ↔ **sota-check: SOTA check — verify "current best" against the live web, not dated memory > The check (fast)**
- `0.832` **game-dev: game-dev — build a game that plays well and can be balanced > Composes with** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > When to use**
- `0.830` **ltx-farm: ltx-farm — drive the local LTX-2.3 render farm > Scriptable IC-LoRA queueing + server hygiene (night-2, 2026-07-06)** ↔ **overnight-studio: Overnight studio — brief → generate → judge → assemble, unattended > Night-2 additions (2026-07-06 — each cost real render time)**
- `0.829` **launching: launching > Channel rules (the expensive lessons)** ↔ **posting-to-socials: posting-to-socials > Common mistakes**
- `0.828` **essay-cuts: essay-cuts > 1. Draft units (main loop, not delegated)** ↔ **posting-to-socials: posting-to-socials > X / Twitter**
- `0.827` **monument: (untitled) > The pipeline (five phases) > Phase 1 — Divergent discovery (temperature = max, go far afield)** ↔ **search-council: search-council > The panel**
- `0.826` **launching: launching > Channel rules (the expensive lessons)** ↔ **posting-to-socials: posting-to-socials > Quick reference**
- `0.825` **game-dev: game-dev — build a game that plays well and can be balanced > The spine (each step composes with build-loop's research→plan→build→test→review)** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > The 7 dimensions**
- `0.824` **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** ↔ **sota-check: SOTA check — verify "current best" against the live web, not dated memory > Common mistakes**
- `0.823` **assumption-audit: (untitled) > Discipline** ↔ **sota-check: SOTA check — verify "current best" against the live web, not dated memory > Staleness cutoffs**
- `0.817` **ltx-farm: ltx-farm — drive the local LTX-2.3 render farm > Storyboard gate + finishing (2026-07-16, slancha-studio)** ↔ **video-gen: video-gen — generate, judge, and treat motion footage > Studio-scale addenda (overnight run, 2026-07-05 — 490 clips, 25 films)**
- `0.817` **essay-cuts: essay-cuts** ↔ **social-media-assistant: social-media-assistant > Sequencing (mirrors DISTRIBUTION.md, adapted for scheduling)**
- `0.817` **build-vs-buy: (untitled) > The method > 3 — Score on the axes that actually decide buy-over-build** ↔ **deep-crawl: (untitled) > The three phases > 3 — Synthesize the dossier**
- `0.816` **op-credentials: op-credentials — check the Slancha service worker before asking > Step 2 — find it in 1Password** ↔ **slancha-cred: slancha-cred — the card-catalog + linter for the Slancha vault > When to use**
- `0.816` **posting-to-socials: posting-to-socials > Cross-platform mechanics** ↔ **social-media-assistant: social-media-assistant > Sequencing (mirrors DISTRIBUTION.md, adapted for scheduling)**
- `0.815` **monument: (untitled) > The pipeline (five phases) > Phase 5 — Implementation ledger + follow-through (the monument is not done here)** ↔ **search-council: search-council > Composing it**
- `0.815` **game-dev: game-dev — build a game that plays well and can be balanced > Web / JS specifics (Three.js / Phaser / canvas)** ↔ **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > The 7 dimensions**
- `0.815` **overnight-studio: Overnight studio — brief → generate → judge → assemble, unattended > Night-2 additions (2026-07-06 — each cost real render time)** ↔ **unattended-overnight-ops: Unattended overnight ops — the failure catalog > Design rules that held**
- `0.814` **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** ↔ **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)**
- `0.814` **game-dev-review: game-dev-review — a 7-dimension review pass for a game codebase > Composes with** ↔ **psychographic-eval: Psychographic eval — judge an artifact by who it delights, bores, and alienates > Composes with**
- `0.814` **deep-crawl: (untitled) > Hunt the surprises (the load-bearing section)** ↔ **monument: (untitled) > Scale, honesty, stop conditions (so it's a monument, not a mess)**
- `0.813` **ltx-farm: ltx-farm — drive the local LTX-2.3 render farm > Storyboard gate + finishing (2026-07-16, slancha-studio)** ↔ **video-finishing: video-finishing — verified keeper finishing > Live chain**
- `0.813` **barkeep: barkeep — route spendy work onto idle pools; run other CLIs as workers > Hands-off draining — the lock-in harvester** ↔ **build-loop: Build loop > Cross-provider runner**
- `0.811` **overnight-studio: Overnight studio — brief → generate → judge → assemble, unattended** ↔ **video-gen: video-gen — generate, judge, and treat motion footage > LTX-2.3 slop patterns (Dell, 2026-07-03 — cost 6 retakes)**
- `0.810` **build-vs-buy: (untitled) > The method > 2 — Enumerate the off-the-shelf options (don't guess)** ↔ **sota-check: SOTA check — verify "current best" against the live web, not dated memory > Composes with**
- `0.809` **overnight-studio: Overnight studio — brief → generate → judge → assemble, unattended > Common mistakes** ↔ **unattended-overnight-ops: Unattended overnight ops — the failure catalog > Design rules that held**
- `0.809` **op-credentials: op-credentials — check the Slancha service worker before asking > Hard rules** ↔ **slancha-cred: slancha-cred — the card-catalog + linter for the Slancha vault > Key facts (so you read the output right)**
- `0.809` **chatterbox-tts: chatterbox-tts — local VO with voice cloning > Usage (VO for video)** ↔ **overnight-studio: Overnight studio — brief → generate → judge → assemble, unattended > The narrative layer — the b-roll factory alone makes MOOD PIECES, not STATEMENTS > VO + caption gotchas (each cost a real debug cycle night-3)**
