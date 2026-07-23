from pathlib import Path

import numpy as np
import pytest

from experiments.skill_decomposer_matcher import (
    Analysis,
    Cluster,
    Section,
    Match,
    MatchConfig,
    analyze_corpus,
    build_clusters,
    decompose_skill,
    match_sections,
    render_markdown,
    threshold_matches,
)


def test_decompose_skill_tracks_heading_path_and_ignores_fenced_headings(tmp_path: Path):
    source = tmp_path / "example" / "SKILL.md"
    source.parent.mkdir()
    source.write_text(
        """---
name: example
description: Example skill.
---

# Example

Opening text that is long enough to retain as a section for this test.

## Verify

Run the focused test, inspect the result, and stop when the evidence is clean.

````markdown
# This is code, not a section
```
# This is still code because the outer fence uses four backticks
````

    # This is indented code, not a section
    ```
   \t~~~

### Failure path

Record the failing command and diagnose the cause before another attempt.
""",
        encoding="utf-8",
    )

    sections = decompose_skill(source, min_chars=20)

    assert [section.heading for section in sections] == [
        "Example",
        "Example > Verify",
        "Example > Verify > Failure path",
    ]
    assert "This is code, not a section" in sections[1].body
    assert "This is still code" in sections[1].body
    assert "This is indented code" in sections[1].body
    assert "```" in sections[1].body
    assert "~~~" in sections[1].body


def test_decompose_skill_rejects_invalid_utf8(tmp_path: Path):
    source = tmp_path / "invalid" / "SKILL.md"
    source.parent.mkdir()
    source.write_bytes(b"# Invalid\n\xff")

    with pytest.raises(UnicodeDecodeError):
        decompose_skill(source)


def test_match_sections_returns_only_cross_skill_neighbors():
    sections = [
        Section("a", "Verify", "a", Path("a/SKILL.md"), 1),
        Section("a", "Stop", "b", Path("a/SKILL.md"), 2),
        Section("b", "Verification", "c", Path("b/SKILL.md"), 1),
    ]
    vectors = np.array([
        [1.0, 0.0],
        [0.99, 0.01],
        [1.0, 0.0],
    ])

    matches = match_sections(sections, vectors, neighbors=2, min_score=0.5)

    assert [(match.left.skill, match.right.skill) for match in matches] == [
        ("a", "b"),
        ("a", "b"),
    ]
    assert matches[0].score == 1.0


def test_build_clusters_requires_three_distinct_skills():
    sections = [
        Section("a", "Verify", "a", Path("a/SKILL.md"), 1),
        Section("b", "Verify", "b", Path("b/SKILL.md"), 1),
        Section("c", "Verify", "c", Path("c/SKILL.md"), 1),
        Section("x", "Setup", "x", Path("x/SKILL.md"), 1),
        Section("y", "Setup", "y", Path("y/SKILL.md"), 1),
    ]
    vectors = np.array([
        [1.0, 0.0],
        [0.99, 0.01],
        [0.98, 0.02],
        [0.0, 1.0],
        [0.01, 0.99],
    ])
    matches = match_sections(sections, vectors, neighbors=2, min_score=0.9)

    clusters = build_clusters(sections, matches, min_skills=3)

    assert len(clusters) == 1
    assert {section.skill for section in clusters[0].sections} == {"a", "b", "c"}


def test_build_clusters_rejects_similarity_chains_without_all_pair_matches():
    alpha = Section("alpha", "Verify", "a", Path("alpha/SKILL.md"), 1)
    beta = Section("beta", "Verify", "b", Path("beta/SKILL.md"), 1)
    gamma = Section("gamma", "Verify", "c", Path("gamma/SKILL.md"), 1)
    matches = [Match(alpha, beta, 0.9), Match(beta, gamma, 0.9)]

    clusters = build_clusters([alpha, beta, gamma], matches, min_skills=3)

    assert clusters == []


def test_build_clusters_returns_bounded_three_skill_evidence_not_maximal_cliques():
    sections = [
        Section(str(index), "Workflow", str(index), Path(str(index)) / "SKILL.md", 1)
        for index in range(5)
    ]
    matches = [
        Match(sections[left], sections[right], 0.9)
        for left in range(len(sections))
        for right in range(left + 1, len(sections))
    ]

    clusters = build_clusters(sections, matches, min_skills=3)

    assert len(clusters) == 10
    assert all(len(cluster.sections) == 3 for cluster in clusters)
    assert len(build_clusters(sections, matches, min_skills=3, max_clusters=4)) == 4
    with pytest.raises(ValueError, match="max_clusters"):
        build_clusters(sections, matches, min_skills=3, max_clusters=0)


def test_triangle_search_uses_all_threshold_edges_not_only_display_neighbors():
    skills = ("alpha", "beta", "gamma", "alpha-decoy", "beta-decoy", "gamma-decoy")
    sections = [Section(skill, "Workflow", skill, Path(skill) / "SKILL.md", 1) for skill in skills]
    vectors = np.array([
        [1.0, 0.0, 0.0],
        [0.8, 0.6, 0.0],
        [0.8, 0.0, 0.6],
        [1.0, 0.0, 0.0],
        [0.8, 0.6, 0.0],
        [0.8, 0.0, 0.6],
    ])

    display_matches = match_sections(sections, vectors, neighbors=1, min_score=0.6)
    all_matches = threshold_matches(sections, vectors, min_score=0.6)
    clusters = build_clusters(sections, all_matches, min_skills=3)

    target_skills = {"alpha", "beta", "gamma"}
    assert not any({match.left.skill, match.right.skill} <= target_skills
                   for match in display_matches)
    assert any(target_skills <= {section.skill for section in cluster.sections}
               for cluster in clusters)


class _SameVectorEmbedder:
    def embed(self, texts):
        return [np.array([1.0, 0.0]) for _ in texts]


def test_analyze_corpus_produces_a_reproducible_cluster_report(tmp_path: Path):
    for skill in ("alpha", "beta", "gamma"):
        skill_dir = tmp_path / skill
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"""---
name: {skill}
description: {skill} skill.
---

# Review and verify

Inspect the proposed change, run focused checks, and record the evidence before approval.
""",
            encoding="utf-8",
        )

    analysis = analyze_corpus(
        tmp_path,
        _SameVectorEmbedder(),
        MatchConfig(min_chars=20, neighbors=2, min_score=0.9, min_skills=3),
    )
    report = render_markdown(analysis, tmp_path, top_matches=5)

    assert analysis.skill_count == 3
    assert len(analysis.sections) == 3
    assert len(analysis.clusters) == 1
    assert "3 skills, 3 sections" in report
    assert "alpha: Review and verify" in report


def test_render_markdown_does_not_emit_trailing_whitespace():
    section = Section("alpha", "Workflow", "word " * 100, Path("alpha/SKILL.md"), 1)
    analysis = Analysis(1, (section,), (), (Cluster((section,), 1.0),))

    report = render_markdown(analysis, Path("."), top_matches=5)

    assert all(line == line.rstrip() for line in report.splitlines())
