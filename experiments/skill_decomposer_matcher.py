"""Decompose SKILL.md files and find similar workflow sections across skills."""
from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from dataclasses import dataclass
from heapq import nsmallest
from itertools import combinations
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Section:
    skill: str
    heading: str
    body: str
    source: Path
    line: int


@dataclass(frozen=True)
class Match:
    left: Section
    right: Section
    score: float


@dataclass(frozen=True)
class Cluster:
    sections: tuple[Section, ...]
    mean_score: float


@dataclass(frozen=True)
class Analysis:
    skill_count: int
    sections: tuple[Section, ...]
    matches: tuple[Match, ...]
    clusters: tuple[Cluster, ...]


@dataclass(frozen=True)
class MatchConfig:
    min_chars: int = 120
    neighbors: int = 3
    min_score: float = 0.78
    min_skills: int = 3
    max_clusters: int = 100


def _without_frontmatter(lines: list[str]) -> tuple[list[str], int]:
    if not lines or lines[0].strip() != "---":
        return lines, 1
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[index + 1 :], index + 2
    return lines, 1


def _heading(line: str) -> tuple[int, str] | None:
    if line.startswith("\t") or len(line) - len(line.lstrip(" ")) > 3:
        return None
    stripped = line.lstrip()
    hashes = len(stripped) - len(stripped.lstrip("#"))
    if not 1 <= hashes <= 6:
        return None
    if len(stripped) == hashes:
        return None
    if stripped[hashes] != " ":
        return None
    title = stripped[hashes + 1 :].strip().rstrip("#").rstrip()
    return (hashes, title) if title else None


def _fence_marker(line: str) -> tuple[str, int, str] | None:
    stripped = line.lstrip(" ")
    if stripped.startswith("\t") or len(line) - len(stripped) > 3:
        return None
    if not stripped or stripped[0] not in ("`", "~"):
        return None
    marker = stripped[0]
    width = len(stripped) - len(stripped.lstrip(marker))
    return (marker, width, stripped[width:]) if width >= 3 else None


class _SectionParser:
    def __init__(self, first_line: int):
        self.first_line = first_line
        self.heading_path: list[str] = []
        self.active_heading = ""
        self.active_line = first_line
        self.body: list[str] = []
        self.fence: tuple[str, int] | None = None
        self.chunks: list[tuple[str, int, str]] = []

    def parse(self, lines: list[str]) -> list[tuple[str, int, str]]:
        for offset, line in enumerate(lines):
            self._consume(offset, line)
        self._flush()
        return self.chunks

    def _consume(self, offset: int, line: str) -> None:
        marker = _fence_marker(line)
        if self.fence:
            self._consume_fenced(line, marker)
        elif marker:
            self.fence = marker[:2]
            self.body.append(line)
        else:
            self._consume_markdown(offset, line)

    def _consume_fenced(self, line: str, marker: tuple[str, int, str] | None) -> None:
        self.body.append(line)
        if marker and self._closes_fence(marker):
            self.fence = None

    def _closes_fence(self, marker: tuple[str, int, str]) -> bool:
        assert self.fence is not None
        same_marker = marker[0] == self.fence[0]
        wide_enough = marker[1] >= self.fence[1]
        return same_marker and wide_enough and not marker[2].strip()

    def _consume_markdown(self, offset: int, line: str) -> None:
        parsed = _heading(line)
        if parsed:
            self._start_section(offset, *parsed)
        else:
            self.body.append(line)

    def _start_section(self, offset: int, level: int, title: str) -> None:
        self._flush()
        self.heading_path[level - 1 :] = []
        self.heading_path.extend(["(untitled)"] * (level - 1 - len(self.heading_path)))
        self.heading_path.append(title)
        self.active_heading = " > ".join(self.heading_path)
        self.active_line = self.first_line + offset
        self.body = []

    def _flush(self) -> None:
        text = "\n".join(self.body).strip()
        if self.active_heading:
            self.chunks.append((self.active_heading, self.active_line, text))


def decompose_skill(source: Path, min_chars: int = 120) -> list[Section]:
    raw_lines = source.read_text(encoding="utf-8").splitlines()
    lines, first_line = _without_frontmatter(raw_lines)
    chunks = _SectionParser(first_line).parse(lines)
    return [
        Section(source.parent.name, heading, body, source, line)
        for heading, line, body in chunks
        if len(body) >= min_chars
    ]


def match_sections(
    sections: list[Section],
    vectors: np.ndarray,
    *,
    neighbors: int,
    min_score: float,
) -> list[Match]:
    matches = threshold_matches(sections, vectors, min_score=min_score)
    selected = {
        match
        for section in sections
        for match in _section_matches(section, matches)[:neighbors]
    }
    return sorted(selected, key=_match_sort_key)


def threshold_matches(
    sections: list[Section],
    vectors: np.ndarray,
    *,
    min_score: float,
) -> list[Match]:
    if len(sections) != len(vectors):
        raise ValueError("one vector is required for every section")
    if not sections:
        return []
    matrix = np.array(vectors, dtype=np.float32, copy=True)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8
    scores = matrix @ matrix.T
    matches = [
        Match(sections[left], sections[right], round(float(scores[left, right]), 6))
        for left, right in combinations(range(len(sections)), 2)
        if sections[left].skill != sections[right].skill
        and scores[left, right] >= min_score
    ]
    return sorted(matches, key=_match_sort_key)


def _section_matches(section: Section, matches: list[Match]) -> list[Match]:
    incident = [match for match in matches if section in (match.left, match.right)]
    return sorted(incident, key=_match_sort_key)


def _match_sort_key(match: Match) -> tuple:
    return (-match.score, match.left.skill, match.left.heading,
            match.right.skill, match.right.heading)


def build_clusters(
    sections: list[Section],
    matches: list[Match],
    *,
    min_skills: int,
    max_clusters: int = 100,
) -> list[Cluster]:
    if min_skills != 3:
        raise ValueError("candidate search requires exactly three skills")
    if max_clusters < 1:
        raise ValueError("max_clusters must be positive")
    neighbors, score_by_edge = _match_graph(sections, matches)
    clusters = (
        _cluster(triangle, sections, score_by_edge)
        for triangle in _triangles(neighbors)
    )
    return nsmallest(max_clusters, clusters, key=_cluster_sort_key)


def _match_graph(
    sections: list[Section],
    matches: list[Match],
) -> tuple[dict[int, set[int]], dict[tuple[int, int], float]]:
    index_by_section = {section: index for index, section in enumerate(sections)}
    neighbors = {index: set() for index in range(len(sections))}
    score_by_edge: dict[tuple[int, int], float] = {}
    for match in matches:
        left = index_by_section[match.left]
        right = index_by_section[match.right]
        neighbors[left].add(right)
        neighbors[right].add(left)
        score_by_edge[tuple(sorted((left, right)))] = match.score
    return neighbors, score_by_edge


def _triangles(neighbors: dict[int, set[int]]) -> Iterator[set[int]]:
    for left, right in _forward_edges(neighbors):
        for third in _common_successors(neighbors, left, right):
            yield {left, right, third}


def _forward_edges(neighbors: dict[int, set[int]]) -> Iterator[tuple[int, int]]:
    for left in sorted(neighbors):
        for right in sorted(node for node in neighbors[left] if node > left):
            yield left, right


def _common_successors(
    neighbors: dict[int, set[int]],
    left: int,
    right: int,
) -> list[int]:
    return sorted(node for node in neighbors[left] & neighbors[right] if node > right)


def _cluster_sort_key(cluster: Cluster) -> tuple:
    identities = tuple((section.skill, section.heading) for section in cluster.sections)
    return -cluster.mean_score, identities


def _cluster(
    triangle: set[int],
    sections: list[Section],
    score_by_edge: dict[tuple[int, int], float],
) -> Cluster:
    ordered_indices = sorted(triangle)
    edge_scores = [score_by_edge[pair] for pair in combinations(ordered_indices, 2)]
    selected = (sections[index] for index in ordered_indices)
    ordered = tuple(sorted(selected, key=lambda section: (section.skill, section.heading)))
    return Cluster(ordered, round(float(np.mean(edge_scores)), 6))


def _skill_sources(root: Path) -> list[Path]:
    return sorted(
        source for source in root.rglob("SKILL.md")
        if "node_modules" not in source.parts
        and not any(part.startswith(".") for part in source.relative_to(root).parts)
    )


def analyze_corpus(
    root: Path,
    embedder,
    config: MatchConfig,
) -> Analysis:
    sources = _skill_sources(root)
    sections = [
        section
        for source in sources
        for section in decompose_skill(source, min_chars=config.min_chars)
    ]
    if not sections:
        return Analysis(len(sources), (), (), ())
    texts = [f"{section.heading}\n\n{section.body}" for section in sections]
    vectors = np.asarray(list(embedder.embed(texts)), dtype=np.float32)
    all_matches = threshold_matches(
        sections,
        vectors,
        min_score=config.min_score,
    )
    matches = match_sections(
        sections,
        vectors,
        neighbors=config.neighbors,
        min_score=config.min_score,
    )
    clusters = build_clusters(
        sections,
        all_matches,
        min_skills=config.min_skills,
        max_clusters=config.max_clusters,
    )
    return Analysis(len(sources), tuple(sections), tuple(matches), tuple(clusters))


def render_markdown(analysis: Analysis, root: Path, *, top_matches: int) -> str:
    lines = [
        "# Skill decomposer and matcher candidates",
        "",
        f"Corpus: `{root}`",
        "",
        (f"Parsed {analysis.skill_count} skills, {len(analysis.sections)} sections, "
         f"{len(analysis.matches)} cross-skill matches, and {len(analysis.clusters)} clusters."),
        "",
        "Candidate clusters are bounded three-skill similarity triangles. They are retrieval leads, "
        "not proof that a shared workflow exists.",
        "",
        "## Candidate clusters",
    ]
    lines.extend(_cluster_lines(analysis.clusters, root))
    lines.extend(["", "## Strongest section pairs", "", *_match_lines(analysis, top_matches)])
    return "\n".join(lines).rstrip() + "\n"


def _cluster_lines(clusters: tuple[Cluster, ...], root: Path) -> list[str]:
    if not clusters:
        return ["", "No clusters passed the configured threshold."]
    return [
        line
        for index, cluster in enumerate(clusters, start=1)
        for line in _one_cluster_lines(index, cluster, root)
    ]


def _one_cluster_lines(index: int, cluster: Cluster, root: Path) -> list[str]:
    skill_count = len({section.skill for section in cluster.sections})
    heading = f"### Cluster {index}: {skill_count} skills, mean matched cosine {cluster.mean_score:.3f}"
    return ["", heading, "", *(_section_line(section, root) for section in cluster.sections)]


def _section_line(section: Section, root: Path) -> str:
    relative = _relative_source(section.source, root)
    snippet = " ".join(section.body.split())[:240].rstrip()
    return f"- **{section.skill}: {section.heading}** (`{relative}:{section.line}`): {snippet}"


def _match_lines(analysis: Analysis, top_matches: int) -> list[str]:
    return [
        f"- `{match.score:.3f}` **{match.left.skill}: {match.left.heading}** ↔ "
        f"**{match.right.skill}: {match.right.heading}**"
        for match in analysis.matches[:top_matches]
    ]


def _relative_source(source: Path, root: Path) -> Path:
    try:
        return source.relative_to(root)
    except ValueError:
        return source


def _section_record(section: Section, root: Path) -> dict:
    return {
        "skill": section.skill,
        "heading": section.heading,
        "body": section.body,
        "source": str(_relative_source(section.source, root)),
        "line": section.line,
    }


def analysis_record(analysis: Analysis, root: Path) -> dict:
    return {
        "skill_count": analysis.skill_count,
        "section_count": len(analysis.sections),
        "match_count": len(analysis.matches),
        "cluster_count": len(analysis.clusters),
        "matches": [
            {
                "score": match.score,
                "left": _section_record(match.left, root),
                "right": _section_record(match.right, root),
            }
            for match in analysis.matches
        ],
        "clusters": [
            {
                "mean_score": cluster.mean_score,
                "sections": [_section_record(section, root) for section in cluster.sections],
            }
            for cluster in analysis.clusters
        ],
    }


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="skill-library root to scan recursively")
    parser.add_argument("--output", type=Path, required=True, help="Markdown report path")
    parser.add_argument("--json-output", type=Path, help="optional machine-readable result path")
    parser.add_argument("--min-chars", type=int, default=120)
    parser.add_argument("--neighbors", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.78)
    parser.add_argument("--min-skills", type=int, choices=(3,), default=3)
    parser.add_argument("--max-clusters", type=_positive_int, default=100)
    parser.add_argument("--top-matches", type=int, default=50)
    args = parser.parse_args()

    from mcp_server.embedding import build_embedding

    root = args.root.resolve()
    analysis = analyze_corpus(
        root,
        build_embedding(),
        MatchConfig(
            min_chars=args.min_chars,
            neighbors=args.neighbors,
            min_score=args.min_score,
            min_skills=args.min_skills,
            max_clusters=args.max_clusters,
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_markdown(analysis, root, top_matches=args.top_matches),
        encoding="utf-8",
    )
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(analysis_record(analysis, root), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        f"{analysis.skill_count} skills, {len(analysis.sections)} sections, "
        f"{len(analysis.matches)} matches, {len(analysis.clusters)} clusters"
    )


if __name__ == "__main__":
    main()
