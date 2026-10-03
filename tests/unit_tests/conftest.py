"""Shared fixtures for unit tests."""

import json
from pathlib import Path

import pytest

RUN_NAME = "demo-run"
RUN_TIMESTAMP = "20260828_212329"
RUN_ITERATION = 4

_PLOTLY_HTML = (
    "<html><body>"
    '<div id="chart-1" class="plotly-graph-div" style="height:100%; width:100%;"></div>'
    '<script type="text/javascript">window.PLOTLYENV=window.PLOTLYENV || {};'
    'Plotly.newPlot("chart-1", [], {});</script>'
    "</body></html>"
)


def _scoreboard(score: float) -> dict:
    return {
        "criteria": [{"name": "Orthogonality", "evaluated": True, "score": score, "passed": True,
                      "reason": "Dimensions are distinct."}],
        "overall": score,
        "model": "judge-model",
    }


@pytest.fixture
def sibling_run_dir(tmp_path: Path):
    """A synthetic run folder with every sibling artifact kind a saved taxonomy can have.

    Mirrors what ``main.py`` writes for one run (taxonomy, report, documents JSON
    sharing one timestamp; biplots; ``--evaluate`` scoreboards) plus decoys that
    exercise the KTD1 tie-break rules:

    - an older report (exact-timestamp match must win);
    - 2D and 3D biplots for the same stage and iteration (3D must win);
    - two evaluation files whose ``source_file`` both point at the taxonomy
      (tie-break picks the newest embedded timestamp).

    Returns ``(taxonomy_path, taxonomy_name, iteration)``.
    """
    clusters = [
        {
            "id": "1", "name": "Replication Strategy", "description": "How replicas stay consistent.",
            "values": [{"id": "1.1", "label": "Consensus replication", "description": "d",
                        "status": "accepted", "supporting_doc_ids": ["d1"]}],
            "relations": [{"target_id": "2", "type": "constrains", "rationale": "r"}],
        },
        {
            "id": "2", "name": "Storage Location", "description": "Where the source of truth lives.",
            "values": [{"id": "2.1", "label": "Object storage log", "description": "d",
                        "status": "accepted", "supporting_doc_ids": ["d2"]}],
            "relations": [],
        },
    ]
    taxonomy_path = tmp_path / f"{RUN_NAME}_taxonomy_{RUN_TIMESTAMP}.json"
    taxonomy_path.write_text(json.dumps({
        "taxonomy_name": RUN_NAME,
        "mode": "train",
        "iterations": [{"explanation": f"iteration {i}", "clusters": clusters} for i in range(1, RUN_ITERATION + 1)],
    }))

    report = "# Grounded Theory Report\n\n## Narrative Summary\n\nThe space has two decisions.\n\n## Other\n"
    (tmp_path / f"{RUN_NAME}_report_{RUN_TIMESTAMP}.md").write_text(report)
    (tmp_path / f"{RUN_NAME}_report_20260801_000000.md").write_text(report)

    (tmp_path / f"{RUN_NAME}_documents_{RUN_TIMESTAMP}.json").write_text(json.dumps({
        "taxonomy_name": RUN_NAME,
        "documents": [{"id": "d1", "content": "doc one", "category": "Replication Strategy",
                       "value": "Consensus replication", "score": 0.9}],
    }))

    for dims in ("2d", "3d"):
        (tmp_path / f"taxonomy_biplot_{RUN_NAME}_standalone_{RUN_ITERATION}_{dims}.html").write_text(_PLOTLY_HTML)

    for ts, score in (("20260828_213000", 0.7), ("20260828_213508", 0.8)):
        (tmp_path / f"taxonomy_evaluation_{ts}.json").write_text(json.dumps({
            "taxonomy_name": RUN_NAME, "source_file": str(taxonomy_path),
            "iteration": RUN_ITERATION, "scoreboard": _scoreboard(score),
        }))

    return taxonomy_path, RUN_NAME, RUN_ITERATION
