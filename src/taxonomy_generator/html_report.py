"""Compose a unified, self-contained HTML report from a taxonomy run's on-disk artifacts.

Given a saved taxonomy JSON, this module locates its sibling grounded-theory
report (``.md``), biplot (``.html``), evaluation scoreboard (``.json``), and
documents (``.json``) in the same directory (see :func:`discover_siblings`),
then renders a single polished HTML page combining them (see
:func:`render_html_report`). Every sibling is optional and every resolver is
fail-soft: a missing or unmatched artifact never raises, it degrades the
corresponding page section to an explicit "not available" state.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from taxonomy_generator.visualization import _sanitize_name

_TIMESTAMP_RE = re.compile(r"(\d{8}_\d{6})")


def _sanitize_report_name(name: str) -> str:
    """Match main.py's inline sanitizer used for report/documents/taxonomy filenames."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in (name or "taxonomy"))


def _extract_timestamp(path: Path) -> str | None:
    """Extract a ``YYYYMMDD_HHMMSS`` timestamp embedded in a filename, if present."""
    match = _TIMESTAMP_RE.search(path.stem)
    return match.group(1) if match else None


@dataclass
class SiblingMatch:
    """A resolved sibling artifact path, and whether the match was a best-effort tie-break."""

    path: Path
    approximate: bool = False


def _pick_candidate(
    candidates: List[Path], preferred_timestamp: str | None = None
) -> SiblingMatch | None:
    """Pick one candidate per KTD1: exact-timestamp match first, else a logged tie-break.

    The tie-break prefers the candidate whose filename carries a parseable
    embedded timestamp (newest such timestamp), falling back to most-recently
    -modified only when no candidate's filename carries one -- a filesystem
    copy operation can reset modification times, so the embedded timestamp is
    the more reliable signal.
    """
    if not candidates:
        return None
    if len(candidates) == 1:
        return SiblingMatch(candidates[0], approximate=False)

    pool = candidates
    if preferred_timestamp:
        exact = [c for c in candidates if _extract_timestamp(c) == preferred_timestamp]
        if len(exact) == 1:
            return SiblingMatch(exact[0], approximate=False)
        if exact:
            pool = exact

    with_timestamp = [(c, _extract_timestamp(c)) for c in pool]
    timestamped = [(c, ts) for c, ts in with_timestamp if ts]
    if timestamped:
        best = max(timestamped, key=lambda pair: pair[1])[0]
    else:
        best = max(pool, key=lambda c: c.stat().st_mtime)
    return SiblingMatch(best, approximate=True)


def resolve_report_path(
    directory: Path, taxonomy_name: str, taxonomy_timestamp: str | None
) -> SiblingMatch | None:
    """Locate the sibling grounded-theory report ``.md`` for a taxonomy JSON."""
    pattern = f"{_sanitize_report_name(taxonomy_name)}_report_*.md"
    candidates = sorted(directory.glob(pattern))
    return _pick_candidate(candidates, preferred_timestamp=taxonomy_timestamp)


def resolve_documents_path(
    directory: Path, taxonomy_name: str, taxonomy_timestamp: str | None
) -> SiblingMatch | None:
    """Locate the sibling documents ``.json`` for a taxonomy JSON.

    ``run()`` writes the documents JSON with the exact same timestamp as the
    taxonomy JSON in the same call, so an exact-timestamp match (KTD1's
    general tie-break rule) is preferred here too, same as the report.
    """
    pattern = f"{_sanitize_report_name(taxonomy_name)}_documents_*.json"
    candidates = sorted(directory.glob(pattern))
    return _pick_candidate(candidates, preferred_timestamp=taxonomy_timestamp)


def resolve_biplot_path(
    directory: Path, taxonomy_name: str, iteration: int
) -> SiblingMatch | None:
    """Locate the sibling biplot ``.html`` for a taxonomy JSON's resolved iteration.

    Prefers a ``standalone``-stage match, else the newest stage. When both a
    2D and 3D variant match the same stage and iteration, prefers 3D as the
    richer view (KTD1).
    """
    pattern = f"taxonomy_biplot_{_sanitize_name(taxonomy_name)}_*_{iteration}*.html"
    candidates = sorted(directory.glob(pattern))
    if not candidates:
        return None

    standalone = [c for c in candidates if f"_standalone_{iteration}" in c.stem]
    pool = standalone or candidates

    three_d = [c for c in pool if c.stem.endswith("_3d")]
    if three_d:
        pool = three_d

    return _pick_candidate(pool)


def _evaluation_matches_source(data: Dict[str, Any], taxonomy_path: Path) -> bool:
    """Compare an evaluation artifact's ``source_file`` to the given taxonomy path by basename."""
    source_file = data.get("source_file")
    if not isinstance(source_file, str) or not source_file:
        return False
    return Path(source_file).name == taxonomy_path.name


def resolve_evaluation_path(
    directory: Path, taxonomy_path: Path, taxonomy_name: str, iteration: int
) -> SiblingMatch | None:
    """Locate the sibling evaluation scoreboard ``.json`` for a taxonomy JSON.

    Prefers an exact match on the file's own ``source_file`` field, falling
    back to ``taxonomy_name`` + ``iteration`` equality. Multi-file
    consistency-mode artifacts (``source_files``/``consistency`` shape, no
    ``source_file`` key) never match this resolver and correctly fall
    through to "no match" (KTD1).
    """
    single_file_candidates: List[Path] = []
    for candidate in sorted(directory.glob("*.json")):
        try:
            data = json.loads(candidate.read_text())
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or "source_file" not in data:
            continue
        single_file_candidates.append((candidate, data))

    exact = [c for c, data in single_file_candidates if _evaluation_matches_source(data, taxonomy_path)]
    if exact:
        return _pick_candidate(sorted(exact))

    fallback = [
        c
        for c, data in single_file_candidates
        if data.get("taxonomy_name") == taxonomy_name and data.get("iteration") == iteration
    ]
    if fallback:
        return _pick_candidate(sorted(fallback))

    return None


@dataclass
class SiblingArtifacts:
    """The four sibling artifacts resolved for one taxonomy JSON, each optional."""

    report: SiblingMatch | None
    biplot: SiblingMatch | None
    evaluation: SiblingMatch | None
    documents: SiblingMatch | None


def discover_siblings(taxonomy_path: Path, taxonomy_name: str, iteration: int) -> SiblingArtifacts:
    """Resolve all four sibling artifacts for a saved taxonomy JSON (KTD1)."""
    directory = taxonomy_path.resolve().parent
    taxonomy_timestamp = _extract_timestamp(taxonomy_path)
    return SiblingArtifacts(
        report=resolve_report_path(directory, taxonomy_name, taxonomy_timestamp),
        biplot=resolve_biplot_path(directory, taxonomy_name, iteration),
        evaluation=resolve_evaluation_path(directory, taxonomy_path, taxonomy_name, iteration),
        documents=resolve_documents_path(directory, taxonomy_name, taxonomy_timestamp),
    )
