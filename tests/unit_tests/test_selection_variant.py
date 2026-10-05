"""benchmark/selection_variant.py: the relevance-filter-off view rebuilt from a saved run (no LLM)."""

import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "selection_variant", Path(__file__).resolve().parents[2] / "benchmark" / "selection_variant.py")
selection_variant = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(selection_variant)


def _dim(dim_id, sources, candidates):
    values = [{"id": f"{dim_id}.{i}", "label": f"v{i}", "status": "accepted"} for i in range(1, candidates + 1)]
    return {"id": dim_id, "name": f"Dim {dim_id}", "values": values,
            "evidence": {"codes": 3, "documents": 3, "sources": sources}}


RUN = {"iterations": [{"clusters": []}, {"clusters": [_dim("1", 3, 2), _dim("2", 1, 2), _dim("3", 3, 1),
                                                      _dim("4", 2, 3)]}],
       "selected_clusters": [_dim("1", 3, 2)], "dropped_dimensions": [{"id": "4", "rationale": "irrelevant"}]}


def test_derive_keeps_every_structurally_valid_dimension():
    out = selection_variant.derive(RUN, min_sources=2, min_candidates=2)
    assert [c["id"] for c in out["selected_clusters"]] == ["1", "4"]
    assert {d["id"] for d in out["dropped_dimensions"]} == {"2", "3"}
    assert out["relevance_selection"] is False and RUN["selected_clusters"][0]["id"] == "1"


def test_cli_writes_a_norelevance_sibling(tmp_path):
    run_path = tmp_path / "c2-x_taxonomy_20260101_000000.json"
    run_path.write_text(json.dumps(RUN))
    cfg = tmp_path / "c.yaml"
    cfg.write_text("taxonomy:\n  min_dimension_sources: 2\n  min_candidate_decisions: 2\n")
    assert selection_variant.main([str(run_path), "--config", str(cfg)]) == 0
    out = json.loads((tmp_path / "c2-x-norelevance_taxonomy_20260101_000000.json").read_text())
    assert [c["id"] for c in out["selected_clusters"]] == ["1", "4"]
