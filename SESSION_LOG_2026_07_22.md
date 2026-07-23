# Session log, 2026-07-22

## What changed

- Added a reproducible `SKILL.md` section decomposer and semantic matcher experiment.
- Added parser, cross-skill matching, and clique-grouping tests.
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
  now require a three-skill clique, which blocks weak-link chains.
- Treat semantic retrieval as proposal generation. Human or model relationship classification
  remains required before extracting a meta-skill.

## Evidence

- Focused tests: `5 passed` in Docker.
- Corpus run: 48 skills, 392 sections, 182 matches, seven cliques.
- Human validation: four accepted raw cliques, three rejected; accepted cliques collapse to three
  unique meta-skill candidates.

## Artifacts

- `experiments/skill_decomposer_matcher.py`: experiment CLI and matching logic.
- `tests/test_skill_decomposer_matcher.py`: parser, matcher, and anti-chain tests.
- `research/skill-decomposer-matcher/candidates.md`: generated candidate report.
- `research/skill-decomposer-matcher/VALIDATION.md`: manual validation and product implications.
