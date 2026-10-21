"""benchmark/evaluation_report.py: run tables over seeds and a run turned into a ground-truth reference."""

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("evaluation_report_cli", ROOT / "benchmark" / "evaluation_report.py")
er = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = er
spec.loader.exec_module(er)
fmt_spec = importlib.util.spec_from_file_location("gt_format_cli", ROOT / "benchmark" / "gt_format.py")
gt_format = importlib.util.module_from_spec(fmt_spec)
fmt_spec.loader.exec_module(gt_format)

CLUSTERS = [{"id": "1", "name": "Replica topology", "description": "How many replicas?",
             "values": [{"id": "1.1", "label": "Three replicas", "description": "", "status": "accepted"},
                        {"id": "1.2", "label": "Fewer outages", "description": "", "status": "outcome"}]},
            {"id": "2", "name": "Write coordination", "description": "How are writes agreed?",
             "values": [{"id": "1.1", "label": "Majority vote", "description": "d", "status": "rejected"}]}]


def _run(tmp, row, seed, values, tokens, *, f1=None, status="ok"):
    folder = tmp / row
    folder.mkdir()
    clusters = [{**CLUSTERS[0], "values": CLUSTERS[0]["values"][:values]}]
    tax = folder / f"c1-ml-workflow-full-s{seed}_taxonomy_20261017_000000.json"
    tax.write_text(json.dumps({
        "selected_clusters": clusters, "iterations": [{"clusters": clusters}], "run_metrics":
        {"total_tokens": tokens, "elapsed_seconds": 120.0}, "evaluation": {"overall": 0.5, "criteria": [
            {"name": "Value exclusivity", "score": 0.25, "evaluated": True}]},
        "operation_log": [{"node": "value_recoding", "before": 0.2, "after": 0.3, "recoded": [{"dimension_id": "1"}]}]}))
    entry = {"row": row, "case": "c1-ml-workflow", "variant": "full", "seed": str(seed), "status": status,
             "taxonomy": str(tax), "match_selected": "", "match_final": ""}
    if f1 is not None:
        metrics = folder / "m_gt_metrics.json"
        part = {"option": {"precision": f1, "recall": f1, "f1": f1}, "decision": {
            "strict": {"f1": f1}, "lenient": {"f1": f1}}, "placement": {"accuracy": 1.0}}
        metrics.write_text(json.dumps({"paper": part, "model": part, "settings": {}}))
        entry["match_selected"] = str(metrics)
    return entry


def _log(path, entries):
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(entries[0]))
        writer.writeheader()
        writer.writerows(entries)


def test_summary_aggregates_seeds_and_keeps_the_latest_successful_run(tmp_path):
    entries = [_run(tmp_path, "M1", 42, 1, 100, f1=0.4), _run(tmp_path, "M2", 43, 2, 300, f1=0.6),
               {**_run(tmp_path, "M2b", 43, 2, 999, status="failed-run"), "row": "M2"}]
    _log(tmp_path / "runs.csv", entries)
    ok = er.latest_ok(tmp_path / "runs.csv")
    assert [e["row"] for e in ok] == ["M1", "M2"] and ok[1]["status"] == "ok"
    records = [er.run_record(e) for e in ok]
    assert records[0]["recoded"] == 1 and records[0]["crit:Value exclusivity"] == 0.25
    [group] = er.aggregate(records)
    assert group["n"] == 2 and group["total_tokens"] == {"mean": 200, "min": 100, "max": 300, "n": 2}
    assert group["selected/paper:option_f1"]["mean"] == 0.5
    md = er.write_summary(records, tmp_path / "report").read_text()
    assert "0.50 [0.40–0.60]" in md and "## Ground truth: paper view" in md


def test_a_run_as_reference_is_a_valid_ground_truth_without_outcomes():
    gt = er.taxonomy_to_gt(CLUSTERS, "c1-ml-workflow", "run.json")
    errors, _warnings = gt_format.validate(gt)
    assert errors == []
    assert [d["id"] for d in gt["decisions"]] == ["D1", "D2"]
    assert [o["id"] for o in gt["options"]] == ["V1_1.1", "V2_1.1"]        # unique although the value ids repeat
    assert len(er.taxonomy_to_gt(CLUSTERS, "c1", "r", include_outcomes=True)["options"]) == 3
