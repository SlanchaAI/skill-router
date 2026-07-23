# Skill decomposer and matcher validation

## Question

Can cheap section-level semantic search surface repeated workflows that deserve extraction into
shared meta-skills?

## Method

- Corpus: 48 first-party skills from `/Users/laul_pogan/Source/dotfiles-claude/skills`.
- Decomposition: Markdown heading sections, excluding frontmatter and headings inside code fences.
- Filter: section body at least 120 characters.
- Embedding: local `BAAI/bge-small-en-v1.5`; no API or model judge.
- Search: each section's three closest sections from other skills, cosine at least `0.78`.
- Grouping: a candidate requires a three-skill clique. Every section must match every other
  section. This rejects weak-link similarity chains.
- Human gate: classify each clique as a repeated workflow, complementary stages, shared policy, or
  topical similarity.

Run result: 48 skills, 392 sections, 182 cross-skill pairs, seven candidate cliques.

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

Raw cluster 5.

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

Raw cluster 6.

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

Raw clusters 3 and 7 match `build-vs-buy`, `deep-crawl`, and `monument`. They share research and
evaluation vocabulary, but their procedures differ: score a purchase decision, inspect a vendor,
and enforce coverage limits. Extracting them would create a vague checklist instead of a reusable
workflow.

Relationship: topical similarity plus shared policy.

### 5. Reject: complementary lifecycle stages are not repetition

Raw cluster 4 matches dossier synthesis, monument stop conditions, and follow-through status
classification. These stages compose sequentially but do not repeat the same procedure.

Relationship: complementary steps.

## Result

The cheap matcher works as a candidate generator, not an automatic decomposer.

- Four of seven raw cliques survived human review.
- Two accepted cliques duplicate the same workflow.
- Final yield: three unique meta-skill candidates.
- Three raw cliques were false positives for extraction.
- Raw clique precision in this run: `4 / 7 = 57%`.
- Unique-candidate yield: three from 48 skills.
- Recall is unknown because the corpus has no labeled inventory of repeated workflows.

The strongest failure mode is relation confusion. An embedding can say two sections are related,
but cannot tell whether they duplicate a workflow, implement adjacent stages, share a policy, or
only discuss the same topic.

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
