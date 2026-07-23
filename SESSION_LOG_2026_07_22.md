# Session log, 2026-07-22

## What changed

- Added a reproducible `SKILL.md` section decomposer and semantic matcher experiment.
- Added parser, cross-skill matching, and bounded triangle-grouping tests.
- Ran the experiment against 48 canonical first-party skills using a local embedding model.
- Added machine-generated candidates plus a manual validation report.

## Why

Test whether repeated workflow sections can be discovered cheaply before introducing a component
language or model-heavy extraction step.

## Major decisions

- Used the canonical `dotfiles-claude/skills` corpus instead of this repo's launch-focused demo
  skills.
- Kept the corpus read-only and used local embeddings with no API spend.
- Replaced connected-component clustering after it chained 27 unrelated skills. Candidate groups
  now require a three-skill similarity triangle, which blocks weak-link chains.
- A fresh reviewer found that top-three display pruning could hide valid clique edges. Clique search
  now uses every above-threshold edge; top-three pruning affects report display only.
- A second review found worst-case exponential behavior in maximal-clique search. Candidate search
  now enumerates exact three-skill triangles and retains at most the strongest 100.
- Markdown parsing now rejects indented pseudo-fences and invalid UTF-8 instead of silently
  swallowing later sections or corrupting source text.
- Treat semantic retrieval as proposal generation. Human or model relationship classification
  remains required before extracting a meta-skill.

## Evidence

- Focused tests: `9 passed` in Docker.
- Full suite after the reviewer fixes: `525 passed, 3 skipped` in Docker.
- CodeScene: Code Health `10.0`; pre-commit quality gate passed.
- Corpus run after the reviewer fixes: 48 skills, 392 sections, 182 displayed matches, 14 triangles.
- A second post-fix corpus run reproduced all four counts.
- Latest report SHA-256:
  `6313c5f2b6a201866a9c7580541784a35a88f86479d1f6ff9fcc05284bc80a1c`.
- Human validation: five extraction-worthy raw triangles, one already-factored positive control,
  and eight rejected; extraction-worthy triangles collapse to three unique meta-skill candidates.

## Artifacts

- `experiments/skill_decomposer_matcher.py`: experiment CLI and matching logic.
- `tests/test_skill_decomposer_matcher.py`: parser, matcher, and anti-chain tests.
- `research/skill-decomposer-matcher/candidates.md`: generated candidate report.
- `research/skill-decomposer-matcher/VALIDATION.md`: manual validation and product implications.
