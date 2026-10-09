"""benchmark/focus_compare.py: base vs. variant scores and judge-noise counts."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "focus_compare", Path(__file__).resolve().parents[2] / "benchmark" / "focus_compare.py")
focus_compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(focus_compare)


def _pair(text, gt, label, source, order=""):
    return {"system_text": text, "gt_id": gt, "gt_text": f"{gt} text", "label": label, "label_source": source,
            "order": order}


def test_rejudged_and_label_changes_are_counted_by_source_transition():
    base = [_pair("A › x", "o1", "same", "judge", "sg"), _pair("A › y", "o1", "different", "auto_rank"),
            _pair("A › z", "o2", "different", "auto")]
    variant = [_pair("A › x", "o1", "same", "judge", "sg"),        # cache hit, unchanged
               _pair("A › y", "o1", "broader", "judge", "gs"),     # routed to the judge now: changed
               _pair("A › z", "o2", "different", "auto"),          # unchanged
               _pair("B › x", "o1", "same", "judge", "sg")]        # moved value: new text, re-judged
    out = focus_compare.compare_pairs(base, variant)
    assert out["rejudged"] == 2 and out["unchanged_pairs"] == 3
    assert out["label_changes_on_unchanged"] == 1 and out["by_transition"] == {"auto_rank->judge": 1}


def test_metrics_deltas_per_view():
    base = {"paper": {"option": {"precision": 0.4}, "decision": {"strict": {"f1": 0.5}}}}
    variant = {"paper": {"option": {"precision": 0.45}, "decision": {"strict": {"f1": 0.5}}}}
    rows = focus_compare.compare_metrics(base, variant)["paper"]
    assert rows["Option P"]["delta"] == 0.05 and rows["Decision F1 (strict)"]["delta"] == 0.0
    assert rows["Placement"]["delta"] is None
