"""benchmark/check_c3_reference.py: integrity of the C3 reference data (B7 map, B9 trade-offs)."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_c3_reference", Path(__file__).resolve().parents[2] / "benchmark" / "check_c3_reference.py")
check_c3_reference = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_c3_reference)

PASSAGES = {"s01_p01", "s02_p01"}
CURATED = {"decision-x"}


def _map(**over):
    rows = [
        {"passage_id": "s01_p01", "corpus": "raw", "systems": "GH-FS;GENERAL", "primary": "GH-FS", "basis": "b"},
        {"passage_id": "s02_p01", "corpus": "raw", "systems": "GH-SPOKES", "primary": "GH-SPOKES", "basis": "b"},
        {"passage_id": "decision-x", "corpus": "curated", "systems": "CUR-CONT", "primary": "CUR-CONT", "basis": "b"},
    ]
    rows[0].update(over)
    return rows


def _tradeoff(**over):
    row = {"id": "T1", "tradeoff": "t", "systems": "GH-SPOKES", "qa_favoured": "reliability",
           "qa_sacrificed": "performance efficiency", "explicitness": "stated",
           "passage_ids": "s02_p01", "curated_ids": "decision-x", "found_in": "raw"}
    row.update(over)
    return row


def test_valid_map_without_tradeoff_file_passes():
    assert check_c3_reference.check(PASSAGES, CURATED, _map(), None) == []


def test_valid_map_and_tradeoffs_pass():
    assert check_c3_reference.check(PASSAGES, CURATED, _map(), [_tradeoff()]) == []


def test_status_comment_line_is_skipped(tmp_path):
    f = tmp_path / "m.csv"
    f.write_text("# agent draft, 2026-10-07, author review pending\npassage_id,corpus,systems,primary,basis\n"
                 "s01_p01,raw,GH-FS,GH-FS,b\n", encoding="utf-8")
    assert check_c3_reference.read_rows(f) == [
        {"passage_id": "s01_p01", "corpus": "raw", "systems": "GH-FS", "primary": "GH-FS", "basis": "b"}]


def test_unmapped_passage_is_reported():
    rows = _map()[1:]
    problems = check_c3_reference.check(PASSAGES, CURATED, rows, None)
    assert any("s01_p01" in p and "not mapped" in p for p in problems)


def test_unknown_passage_id_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(passage_id="s09_p09"), None)
    assert any("s09_p09" in p for p in problems)


def test_unknown_system_code_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(systems="GH-FS;BITBUCKET"), None)
    assert any("BITBUCKET" in p for p in problems)


def test_primary_outside_systems_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(primary="GOOG-DHT"), None)
    assert any("primary" in p and "GOOG-DHT" in p for p in problems)


def test_empty_basis_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(basis=" "), None)
    assert any("basis" in p for p in problems)


def test_tradeoff_with_unknown_passage_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(), [_tradeoff(passage_ids="s02_p01;s07_p01")])
    assert any("s07_p01" in p for p in problems)


def test_tradeoff_without_raw_passage_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(), [_tradeoff(passage_ids="")])
    assert any("T1" in p and "raw passage" in p for p in problems)


def test_tradeoff_with_empty_quality_attribute_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(), [_tradeoff(qa_sacrificed="")])
    assert any("qa_sacrificed" in p for p in problems)


def test_tradeoff_with_unknown_curated_id_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(), [_tradeoff(curated_ids="decision-y")])
    assert any("decision-y" in p for p in problems)


def test_tradeoff_with_bad_enum_values_is_reported():
    problems = check_c3_reference.check(PASSAGES, CURATED, _map(),
                                        [_tradeoff(explicitness="guessed", found_in="memory")])
    assert any("explicitness" in p for p in problems) and any("found_in" in p for p in problems)
