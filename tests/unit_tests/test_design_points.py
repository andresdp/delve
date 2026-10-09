"""evaluation/design_points.py: seeded sampling of design points (paper plan A12, E13)."""

import importlib.util
import csv
import json
from pathlib import Path

from taxonomy_generator.evaluation import design_points as dp

_spec = importlib.util.spec_from_file_location(
    "design_points_cli", Path(__file__).resolve().parents[2] / "benchmark" / "design_points.py")
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


def _value(vid, label, status, docs):
    return {"id": vid, "label": label, "status": status, "supporting_doc_ids": docs, "description": label}


def _clusters():
    return [
        {"id": "1", "name": "Source of truth", "relations": [{"target_id": "2", "type": "constrains"}],
         "values": [_value("1.1", "Disk quorum", "accepted", ["a1"]), _value("1.2", "WAL in S3", "accepted", ["c1"]),
                    _value("1.3", "Distributed FS", "rejected", ["f1"])]},
        {"id": "2", "name": "Replication", "relations": [],
         "values": [_value("2.1", "3PC", "accepted", ["a2"]), _value("2.2", "Gossip", "mixed", ["c2"]),
                    _value("2.3", "Fewer reads", "outcome", ["a2"])]},
        {"id": "3", "name": "Compaction", "relations": [],
         "values": [_value("3.1", "Every replica", "accepted", ["a3"]), _value("3.2", "Primary only", "accepted", ["c3"])]},
    ]


SYSTEMS = {"a1": {"SPOKES"}, "a2": {"SPOKES"}, "a3": {"SPOKES"},
           "c1": {"CONT"}, "c2": {"CONT"}, "c3": {"CONT"}, "f1": {"FS"}}


def _labels(point):
    return [v["label"] for v in point["values"]]


def test_attested_points_are_co_supported_by_their_system():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=3, n=10, seed=1)
    attested = out["groups"]["attested"]
    assert {p["system"] for p in attested} == {"SPOKES", "CONT"}
    for p in attested:
        assert all(p["system"] in v["systems"] for v in p["values"])


def test_novel_points_have_no_common_system_and_only_candidate_values():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=2, n=10, seed=1)
    novel = out["groups"]["novel"]
    assert novel
    for p in novel:
        common = set.intersection(*[set(v["systems"]) for v in p["values"]])
        assert not common
        assert all(v["status"] in ("accepted", "mixed") for v in p["values"])


def test_points_use_distinct_dimensions_and_no_duplicates():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=2, n=30, seed=3)
    seen = set()
    for group in out["groups"].values():
        for p in group:
            dims = [v["dimension_id"] for v in p["values"]]
            assert len(set(dims)) == len(dims)
            key = (p["group"], frozenset((v["dimension_id"], v["value_id"]) for v in p["values"]), p.get("control"))
            assert key not in seen
            seen.add(key)


def test_controls_hold_a_rejected_or_misplaced_value():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=2, n=10, seed=2)
    controls = out["groups"]["control"]
    kinds = {p["control"] for p in controls}
    assert kinds == {"rejected_value", "misplaced_value"}
    for p in controls:
        if p["control"] == "rejected_value":
            assert any(v["status"] == "rejected" for v in p["values"])
        else:
            assert any(v["origin_dimension_id"] != v["dimension_id"] for v in p["values"])


def test_outcome_values_are_never_sampled():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=2, n=30, seed=4)
    labels = {label for g in out["groups"].values() for p in g for label in _labels(p)}
    assert "Fewer reads" not in labels


def test_same_seed_same_sample():
    a = dp.sample_design_points(_clusters(), SYSTEMS, k=2, n=5, seed=9)
    b = dp.sample_design_points(_clusters(), SYSTEMS, k=2, n=5, seed=9)
    assert a == b


def test_relations_among_chosen_dimensions_are_recorded():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=3, n=5, seed=1)
    p = out["groups"]["attested"][0]
    assert {"source": "1", "target": "2", "type": "constrains"} in p["relations"]


def test_without_system_map_there_is_no_attested_group():
    out = dp.sample_design_points(_clusters(), None, k=2, n=5, seed=1)
    assert out["groups"]["attested"] == []
    assert out["groups"]["novel"]
    assert out["diagnostics"]["system_map"] is False


def test_k_larger_than_dimensions_yields_nothing_and_a_note():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=4, n=5, seed=1)
    assert all(not g for g in out["groups"].values())
    assert "dimensions" in out["diagnostics"]["note"]


def test_shortfall_is_reported_per_system():
    out = dp.sample_design_points(_clusters(), SYSTEMS, k=3, n=50, seed=1)
    diag = out["diagnostics"]
    assert diag["requested_per_group"] == 50
    assert diag["achieved"]["attested"] < 50
    assert diag["systems"]["SPOKES"]["dimensions"] == 3
    assert diag["systems"]["FS"]["dimensions"] == 0


def test_load_system_map_skips_comments_and_general(tmp_path):
    f = tmp_path / "m.csv"
    f.write_text("# status\npassage_id,corpus,systems,primary,basis\ns01_p01,raw,GH-FS;GENERAL,GH-FS,b\n"
                 "s01_p02,raw,GENERAL,GENERAL,b\n", encoding="utf-8")
    assert dp.load_system_map(f) == {"s01_p01": {"GH-FS"}, "s01_p02": set()}


def test_load_system_map_by_primary_keeps_only_the_main_system(tmp_path):
    f = tmp_path / "m.csv"
    f.write_text("passage_id,corpus,systems,primary,basis\ns01_p15,raw,CUR-CONT;MS-ADO,CUR-CONT,b\n", encoding="utf-8")
    assert dp.load_system_map(f, attest_by="primary") == {"s01_p15": {"CUR-CONT"}}
    assert dp.load_system_map(f, attest_by="systems") == {"s01_p15": {"CUR-CONT", "MS-ADO"}}


def test_cli_writes_points_and_blind_sheet(tmp_path):
    run = tmp_path / "c3_taxonomy_20261008_000000.json"
    run.write_text(json.dumps({"selected_clusters": _clusters()}), encoding="utf-8")
    sysmap = tmp_path / "m.csv"
    rows = "\n".join(f"{d},raw,{';'.join(s)},{next(iter(s))},b" for d, s in SYSTEMS.items())
    sysmap.write_text("passage_id,corpus,systems,primary,basis\n" + rows + "\n", encoding="utf-8")
    assert cli.main([str(run), "--systems", str(sysmap), "--k", "2", "3", "--n", "4", "--seed", "5"]) == 0
    data = json.loads((tmp_path / "c3_taxonomy_20261008_000000_design_points.json").read_text())
    assert {s["k"] for s in data["samples"]} == {2, 3}
    with open(tmp_path / "c3_taxonomy_20261008_000000_design_points_sheet.csv", encoding="utf-8") as f:
        sheet = list(csv.DictReader(f))
    assert sheet and "group" not in sheet[0] and "verdict" in sheet[0]
    ids = {p["point_id"] for s in data["samples"] for g in s["groups"].values() for p in g}
    assert {r["point_id"] for r in sheet} == ids


def _cli_files(tmp_path):
    run = tmp_path / "c3_taxonomy_20261008_000000.json"
    run.write_text(json.dumps({"selected_clusters": _clusters()}), encoding="utf-8")
    sysmap = tmp_path / "m.csv"
    rows = "\n".join(f"{d},raw,{';'.join(s)},{next(iter(s))},b" for d, s in SYSTEMS.items())
    sysmap.write_text("passage_id,corpus,systems,primary,basis\n" + rows + "\n", encoding="utf-8")
    return run, sysmap


def test_cli_describes_points_only_when_asked(tmp_path, monkeypatch):
    import sys
    import types
    calls = []

    async def fake_run(dp_path, model, force, concurrency):
        calls.append((Path(dp_path).name, model))
        return {}

    monkeypatch.setitem(sys.modules, "describe_design_points", types.SimpleNamespace(run=fake_run))
    run, sysmap = _cli_files(tmp_path)
    assert cli.main([str(run), "--systems", str(sysmap), "--k", "2", "--n", "2"]) == 0
    assert calls == [] and not list(tmp_path.glob("*_descriptions.json"))
    assert cli.main([str(run), "--systems", str(sysmap), "--k", "2", "--n", "2", "--describe",
                     "--describe-model", "openai/x"]) == 0
    assert calls == [("c3_taxonomy_20261008_000000_design_points.json", "openai/x")]
