# Skill decomposer and matcher validation

## Question

Can cheap section-level semantic search surface repeated workflows that deserve extraction into
shared meta-skills?

## Method

- Corpus: 48 first-party skills from `/Users/laul_pogan/Source/dotfiles-claude/skills`.
- Decomposition: Markdown heading sections, excluding frontmatter and headings inside code fences.
- Filter: section body at least 120 characters.
- Embedding: local `BAAI/bge-small-en-v1.5`; no API or model judge.
- Search display: each section's three closest sections from other skills, cosine at least `0.78`.
- Grouping: every above-threshold edge participates in triangle search, independent of display
  ranking. A candidate contains exactly three skills whose sections all match each other; the run
  retains the strongest 100. This rejects weak-link chains without exponential clique search.
- Human gate: classify each triangle as a repeated workflow, complementary stages, shared policy, or
  topical similarity.

Run result: 48 skills, 392 sections, 182 displayed cross-skill pairs, 14 candidate triangles.

## Manual verdicts

### 1. Accept: schedule, publish, verify

Raw clusters 1 and 2 represent one workflow, so count them once.

Evidence:

- `essay-cuts`: `5. Schedule (Zernio) + verify`
- `posting-to-socials`: `Tooling (optional)`
- `social-media-assistant`: `Sequencing` and `Zernio client`

Repeated procedure:

1. Choose API scheduling or browser delivery from platform constraints.
2. Read post content from reviewed files.
3. Convert local time to UTC and stagger channels.
4. Schedule each post.
5. Query pending posts to verify content and time.
6. Save the scheduling receipt in the campaign artifact.

Meta-skill candidate: `schedule-and-verify-social-distribution`.

### 2. Accept: bounded fan-out research with one writer

Raw clusters 7 and 14 represent the same workflow.

Evidence:

- `deep-crawl`: `Scaling`
- `monument`: `Phase 3, Deep-crawl EVERYTHING selected`
- `search-council`: `Composing it`

Repeated procedure:

1. Reuse cached evidence before new retrieval.
2. Split independent targets into bounded batches.
3. Give every worker an isolated output path.
4. Workers return evidence; one writer owns synthesis.
5. Cap concurrency and drain one fleet before another.
6. Write results back to the cache.

Meta-skill candidate: `bounded-research-fanout`.

### 3. Accept: canonical-first staggered distribution

Raw cluster 11.

Evidence:

- `launching`: `The sequence`
- `posting-to-socials`: `Cross-platform mechanics`
- `social-media-assistant`: `Sequencing`

Repeated procedure:

1. Publish the canonical artifact.
2. Confirm its URL resolves.
3. Adapt the message per channel.
4. Stagger channel posts over hours or days.
5. Verify each published or scheduled item.
6. Re-amplify later with a different angle.

Meta-skill candidate: `canonical-first-distribution`.

### 4. Reject: evaluation lists are not one workflow

Raw clusters 3, 4, 10, and 13 match `build-vs-buy`, `deep-crawl`, and `monument`. They share
research and evaluation vocabulary, but their procedures differ: enumerate options, score a
purchase decision, inspect a vendor, and enforce coverage limits. Extracting them would create a
vague checklist instead of a reusable workflow.

Relationship: topical similarity plus shared policy.

### 5. Reject: complementary lifecycle stages are not repetition

Raw clusters 5, 6, 9, and 12 match research discovery, dossier synthesis, atlas synthesis, and
follow-through classification. These stages compose sequentially but do not repeat the same
procedure.

Relationship: complementary steps.

### 6. Already factored: source-verified dossier research

Raw cluster 8 matches `build-vs-buy`, `deep-crawl`, and `monument` around enumerating options,
reading primary sources, checking licenses, and producing dossiers. This is a valid shared workflow,
but it is already factored as `deep-crawl`; the other skills call it explicitly.

Relationship: existing meta-skill reuse, not a new extraction candidate.

## Result

The cheap matcher works as a candidate generator, not an automatic decomposer.

- Five of 14 raw triangles were extraction-worthy.
- Those five collapse into three repeated workflows.
- One additional triangle correctly recovered an already-factored workflow, `deep-crawl`.
- Final yield: three unique meta-skill candidates.
- Eight raw triangles were false positives for extraction.
- Raw extraction precision in this run: `5 / 14 = 36%`.
- Unique-candidate yield: three from 48 skills.
- Recall is unknown because the corpus has no labeled inventory of repeated workflows.

The strongest failure mode is relation confusion. An embedding can say two sections are related,
but cannot tell whether they duplicate a workflow, implement adjacent stages, share a policy, or
only discuss the same topic.

The retrieval fix doubled candidate triangles from seven to 14 without changing the three unique new
candidates. It improved recall safety but lowered the human review yield, which confirms that dense
semantic similarity still needs relationship classification.

## Product implication

Useful pipeline:

1. Decompose skills into structural sections.
2. Retrieve cross-skill semantic neighbors.
3. Form dense multi-skill candidates.
4. Classify the relationship: duplicate workflow, complementary step, shared policy, or topic only.
5. Draft a meta-skill only for duplicate workflows.
6. Rewrite source skills to reference the candidate.
7. Run source-skill and assembled-skill evaluations before promotion.

Ingot already supplies the missing governance layer for steps 6 and 7. The decomposer and matcher
should propose shared components; evidence-gated promotion should decide whether they replace
duplicated sections.
