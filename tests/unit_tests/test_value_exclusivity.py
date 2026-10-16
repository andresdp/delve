"""Value exclusivity: the measure, the scoreboard penalty, the repair step, the cap at selection and the wiki."""

import asyncio
from types import SimpleNamespace

import pytest

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.evaluation import exclusivity as ex
from taxonomy_generator.evaluation import runner as runner_module
from taxonomy_generator.nodes.dimension_selector import _without_relevance_filter, apply_cap
from taxonomy_generator.nodes.exclusivity_repair import merge_candidates, repair_exclusivity
from taxonomy_generator.schemas import ExclusivityAction, ExclusivityPart, ExclusivityRepairOutput
from taxonomy_generator.settings import load_settings
from taxonomy_generator.utils import format_evaluation_summary
from taxonomy_generator.wiki import build
from tests.unit_tests.test_scoreboard_runner import _config, _fake_build_metrics
from tests.unit_tests.test_wiki_export import _inputs


def _v(vid, label, accepted=(), rejected=(), status=None, stances=True):
    status = status or ("mixed" if accepted and rejected else "rejected" if rejected else "accepted")
    v = {"id": vid, "label": label, "description": f"{label}.", "status": status,
         "supporting_doc_ids": sorted(set(accepted) | set(rejected)), "evidence_code_count": 1}
    if stances:
        v["stances"] = {k: list(d) for k, d in (("accepted", accepted), ("rejected", rejected)) if d}
    return v


def _dim(did, name, values, **extra):
    return {"id": did, "name": name, "description": f"{name}?", "relations": [], "values": values, **extra}


def _commit():
    """s01 and s02 adopt both 1.1 and 1.2 (features, not alternatives); s03 adopts 1.3 only."""
    return _dim("1", "Replica commit", [
        _v("1.1", "Three-phase commit", accepted=["s01_p01", "s02_p01"]),
        _v("1.2", "Reference locking", accepted=["s01_p02", "s02_p01"]),
        _v("1.3", "Majority vote", accepted=["s03_p01"]),
        _v("1.4", "Write availability", accepted=["s03_p01"], status="outcome"),
    ])


# ------------------------------------------------------------------ U1. the measure


def test_exclusivity_counts_sources_that_adopt_several_values():
    row = ex.dimension_exclusivity(_commit())
    assert (row["units"], row["exclusive_units"], row["max_values_per_unit"]) == (3, 1, 2)
    assert row["score"] == pytest.approx(1 / 3)
    assert row["conflicts"] == {"s01": ["1.1", "1.2"], "s02": ["1.1", "1.2"]}
    assert row["pairs"][0]["values"] == ["1.1", "1.2"] and row["pairs"][0]["units"] == ["s01", "s02"]


def test_rejections_outcomes_and_values_without_stances():
    dim = _dim("2", "Storage", [
        _v("2.1", "Plain Git", accepted=["s01_p01"]),
        _v("2.2", "NFS", rejected=["s01_p02"]),                         # rejected: never adoption
        _v("2.3", "DHT", accepted=["s02_p01"], stances=False),          # no stances: accepted status counts
        _v("2.4", "Fast clone", accepted=["s02_p01"], status="outcome"),
    ])
    row = ex.dimension_exclusivity(dim)
    assert row["score"] == 1.0 and row["units"] == 2 and not row["pairs"]


def test_a_declared_hybrid_counts_as_one_choice():
    dim = _commit()
    dim["hybrids"] = [{"value_ids": ["1.1", "1.2"], "reason": "used together by design"}]
    assert ex.dimension_exclusivity(dim)["score"] == 1.0


def test_units_can_be_systems_from_a_passage_map():
    systems = {"s01_p01": {"primary": "A"}, "s01_p02": {"primary": "B"}, "s02_p01": {"primary": "GENERAL"},
               "s03_p01": {"primary": "A"}}
    row = ex.dimension_exclusivity(_commit(), ex.unit_from_system_map(systems))
    assert row["conflicts"] == {"A": ["1.1", "1.3"]} and row["units"] == 2   # GENERAL is no system


def test_taxonomy_score_is_weighted_and_dimensions_without_adopters_are_left_out():
    report = ex.taxonomy_exclusivity([_commit(), _dim("3", "Empty", [_v("3.1", "x", rejected=["s01_p01"])])])
    assert report["score"] == pytest.approx(1 / 3) and report["dimensions"][-1]["score"] is None
    assert ex.taxonomy_exclusivity([])["score"] is None


# ------------------------------------------------------------------ U2. the penalty on the scoreboard


def test_scoreboard_row_names_the_dimension_and_the_fix():
    row = ex.scoreboard_row([_commit()], 0.5)
    assert row["name"] == ex.CRITERION_NAME and row["deterministic"] and row["passed"] is False
    assert "Dimension 1 'Replica commit'" in row["reason"] and "Split such a dimension" in row["reason"]
    assert "passages s01_p01" in row["reason"] and row["fragmentation"]["dimensions"] == 1
    assert ex.scoreboard_row([_dim("9", "None", [])], 0.5) is None


def test_runner_adds_the_row_counts_it_in_overall_and_feeds_it_back(monkeypatch):
    monkeypatch.setattr(runner_module, "build_metrics", _fake_build_metrics)
    board = asyncio.run(runner_module.run_scoreboard([_commit()], None, _config()))
    row = next(r for r in board["criteria"] if r["name"] == ex.CRITERION_NAME)
    judged = [r["score"] for r in board["criteria"] if r.get("evaluated") and r["name"] != ex.CRITERION_NAME]
    assert board["overall"] == pytest.approx((sum(judged) + row["score"]) / (len(judged) + 1))
    assert "Replica commit" in format_evaluation_summary(board)               # the weakest row is fed back
    off = asyncio.run(runner_module.run_scoreboard([_commit()], None,
                                                   SimpleNamespace(**vars(_config()), evaluation_exclusivity=False)))
    assert ex.CRITERION_NAME not in {r["name"] for r in off["criteria"]}


# ------------------------------------------------------------------ U3. the repair step


class FakeModel:
    """Structured-output stand-in: answers each dimension (by its id in the prompt) with a canned proposal."""

    def __init__(self, answers):
        self.answers, self.seen = answers, []

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, messages):
        text = "\n".join(m.content for m in messages)
        did = next(d for d in self.answers if f'"id": "{d}"' in text.split("## Values adopted together")[0])
        self.seen.append(did)
        answer = self.answers[did]
        if isinstance(answer, Exception):
            raise answer
        return answer


def _act(action, value_ids=(), parts=(), name="", description="", reason="because", to=""):
    return ExclusivityAction(action=action, value_ids=list(value_ids), parts=list(parts), name=name, to_dimension_id=to,
                             description=description, reason=reason)


def _repair(clusters, answers, **kw):
    model = FakeModel(answers)
    passages = {"s01_p01": "Spokes uses three-phase commit and locks references.", "s02_p01": "Both, again."}
    out, log = asyncio.run(repair_exclusivity(clusters, model, "Git hosting", passages, **kw))
    return out, log, model


def test_only_dimensions_below_the_threshold_are_sent():
    fine = _dim("2", "Storage", [_v("2.1", "Plain Git", accepted=["s01_p01"]), _v("2.2", "DHT", accepted=["s02_p01"])])
    out, log, model = _repair([_commit(), fine], {"1": ExclusivityRepairOutput(actions=[], rationale="ok"),
                                                  "2": ExclusivityRepairOutput(actions=[], rationale="ok")})
    assert model.seen == ["1"] and log["dimensions"] == ["1"] and log["before"] == log["after"]


def test_extract_moves_a_sub_decision_to_a_dimension_that_refines_the_original():
    clusters = [_commit()]
    answer = ExclusivityRepairOutput(rationale="locking is a mechanism",
                                     actions=[_act("extract", ["1.2", "1.3"], name="Reference locking scope",
                                                   description="How are references locked?")])
    out, log, _ = _repair(clusters, {"1": answer})
    new = next(d for d in out if d["name"] == "Reference locking scope")
    assert [v["label"] for v in new["values"]] == ["Reference locking", "Majority vote"]
    assert {"target_id": "1", "type": "refines"}.items() <= new["relations"][0].items()
    assert log["after"] == 1.0 and log["before"] < 1 and len(log["operations"]) == 1
    assert clusters[0]["values"][1]["id"] == "1.2"                            # the input is not modified


def test_merge_unions_stances_and_evidence():
    answer = ExclusivityRepairOutput(rationale="same option", actions=[_act("merge", ["1.1", "1.2"], name="3PC with locks")])
    out, log, _ = _repair([_commit()], {"1": answer})
    merged = out[0]["values"][0]
    assert merged["label"] == "3PC with locks" and merged["stances"]["accepted"] == ["s01_p01", "s01_p02", "s02_p01"]
    assert merged["merged_from"] == [{"id": "1.2", "label": "Reference locking"}] and log["after"] == 1.0
    assert out[0]["evidence"]["sources"] == 3


def test_split_and_hybrid_and_invalid_proposals():
    dim = _dim("1", "Replica commit", _commit()["values"][:3] + [
        _v("1.5", "Gossip", accepted=["s04_p01"]), _v("1.6", "Raft", accepted=["s01_p03", "s04_p02"])])
    split = _act("split", parts=[ExclusivityPart(name="Commit protocol", description="?", value_ids=["1.1", "1.3", "1.5"]),
                                 ExclusivityPart(name="Locking", description="?", value_ids=["1.2", "1.6"])])
    out, log, _ = _repair([dim], {"1": ExclusivityRepairOutput(rationale="two questions", actions=[split])})
    assert [d["name"] for d in out] == ["Commit protocol", "Locking"] and len(log["operations"]) == 1

    bad_split = _act("split", parts=[ExclusivityPart(name="A", description="?", value_ids=["1.1"]),
                                     ExclusivityPart(name="B", description="?", value_ids=["1.2", "1.3"])])
    hybrid = _act("hybrid", ["1.1", "1.2"], reason="combined by design")
    out, log, _ = _repair([_commit()], {"1": ExclusivityRepairOutput(
        rationale="x", actions=[bad_split, hybrid, _act("merge", ["1.1", "9.9"])])})
    assert len(log["rejected"]) == 2 and out[0]["hybrids"] == [{"value_ids": ["1.1", "1.2"], "reason": "combined by design"}]
    assert log["after"] == 1.0


class SequenceModel(FakeModel):
    """Answers the same dimension with successive proposals (round 1, then the retry), keeping the prompts."""

    def __init__(self, answers):
        super().__init__({})
        self.queue, self.prompts = list(answers), []

    async def ainvoke(self, messages):
        self.prompts.append("\n".join(m.content for m in messages))
        return self.queue.pop(0)


def test_a_rejected_proposal_is_retried_with_the_error_and_moves_and_outcomes_apply():
    other = _dim("2", "Locking", [_v("2.1", "Per-repo lock", accepted=["s05_p01"]), _v("2.2", "Global lock", accepted=["s06_p01"])])
    first = ExclusivityRepairOutput(rationale="locking", actions=[_act("extract", ["1.2"], name="Lock", description="?")])
    retry = ExclusivityRepairOutput(rationale="move it", actions=[_act("move", ["1.2"], to="2")])
    model = SequenceModel([first, retry])
    out, log = asyncio.run(repair_exclusivity([_commit(), other], model, "Git", {}))
    assert len(model.prompts) == 2 and "previous proposal" in model.prompts[1] and "1 candidate" in model.prompts[1]
    assert [o["round"] for o in log["operations"]] == [2] and log["rejected"][0]["round"] == 1
    assert "Reference locking" in [v["label"] for v in out[1]["values"]] and log["after"] == 1.0
    assert log["dimensions_before"] == log["dimensions_after"] == 2              # no new dimension

    as_outcome = ExclusivityRepairOutput(rationale="goal", actions=[_act("outcome", ["1.2"])])
    out, log = asyncio.run(repair_exclusivity([_commit()], SequenceModel([as_outcome]), "Git", {}))
    assert next(v for v in out[0]["values"] if v["label"] == "Reference locking")["status"] == "outcome"


def test_a_failed_call_leaves_the_dimension_unchanged():
    out, log, _ = _repair([_commit()], {"1": RuntimeError("boom")})
    assert log["failed_calls"][0]["dimension_id"] == "1" and [v["id"] for v in out[0]["values"]] == ["1.1", "1.2", "1.3", "1.4"]


def test_merge_candidates_rejects_outcomes_and_unknown_values():
    with pytest.raises(ValueError, match="candidate"):
        merge_candidates(_commit(), ["1.1", "1.4"], "", "")
    with pytest.raises(ValueError, match="not in dimension"):
        merge_candidates(_commit(), ["1.1", "7.7"], "", "")


# ------------------------------------------------------------------ U4. the cap at selection


def test_cap_applies_at_selection_by_default(tmp_path):
    cfg = Configuration(max_num_clusters=5)
    assert cfg.generation_cap is None and cfg.selection_cap == 5           # default: at selection
    assert Configuration(max_num_clusters=5, cap_stage="selection").generation_cap is None
    assert Configuration(max_num_clusters=5, cap_stage="selection").selection_cap == 5
    assert Configuration(max_num_clusters=5, cap_stage="generation").generation_cap == 5
    assert Configuration(max_num_clusters=5, cap_stage="generation").selection_cap is None
    path = tmp_path / "c.yaml"
    path.write_text("taxonomy:\n  cap_stage: sometimes\n")
    with pytest.raises(ValueError, match="cap_stage"):
        load_settings(str(path))


def test_apply_cap_keeps_the_first_k_and_records_the_rest():
    dims = [{"id": str(i)} for i in range(1, 5)]
    kept, dropped = apply_cap(dims, 2)
    assert [d["id"] for d in kept] == ["1", "2"] and [d["id"] for d in dropped] == ["3", "4"]
    assert "Outside the cap of 2" in dropped[0]["rationale"]
    assert apply_cap(dims, None) == (dims, [])


def test_without_relevance_filter_the_cap_ranks_by_sources_then_exclusivity():
    a = {**_commit(), "id": "a", "evidence": {"sources": 3}}                  # exclusivity 1/3
    b = {**_commit(), "id": "b", "evidence": {"sources": 3}, "hybrids": [{"value_ids": ["1.1", "1.2"]}]}   # 1.0
    c = {**_commit(), "id": "c", "evidence": {"sources": 1}}
    result = _without_relevance_filter([a, b, c], [a, b, c], [], cap=2)
    assert [d["id"] for d in result["selected_clusters"][0]] == ["b", "a"]
    assert [d["id"] for d in result["dropped_dimensions"]] == ["c"]


# ------------------------------------------------------------------ U5. the wiki


def test_wiki_shows_exclusivity_by_source_without_a_system_map():
    export = build(_inputs(systems={}))
    dim = next(p for p in export.pages if p.path == "concepts/source-of-truth")
    assert "## Exclusivity" in dim.body and "source" in dim.body and dim.frontmatter["exclusivity"] == 1.0
    node = next(n for n in export.graph["nodes"] if n["id"] == "d:1")
    assert node["exclusivity"] == 1.0


def test_system_pages_split_adopted_and_rejected_values():
    export = build(_inputs())
    fs = next(p for p in export.pages if p.path == "synthesis/systems/fs")
    assert "Considered and rejected" in fs.body
    row = next(line for line in fs.body.splitlines() if "Source of truth" in line)
    adopted, rejected = row.split(" | ")[1], row.split(" | ")[2]
    assert "WAL in S3" not in adopted and "WAL in S3" in rejected


def test_exclusivity_feedback_has_its_own_section_with_whole_lines():
    dims = [_dim(str(i), f"Decision {i}", [_v(f"{i}.1", "a", accepted=["s01_p01", "s02_p01"]),
                                          _v(f"{i}.2", "b", accepted=["s01_p02", "s02_p02"])]) for i in range(1, 5)]
    row = ex.scoreboard_row(dims, 0.5)
    judged = {"name": "Clarity", "score": 0.4, "threshold": 0.5, "reason": "x" * 900, "evaluated": True}
    text = format_evaluation_summary({"criteria": [judged, row], "overall": 0.2})
    assert "Value exclusivity (computed from the evidence, not a judge): 0.00" in text
    assert all(f"Dimension {i} 'Decision {i}'" in text for i in range(1, 5))     # not cut at 700 characters
    assert "do not create dimensions with a single candidate decision" in text
    assert "- Value exclusivity:" not in text                                   # not among the judged issues
    only = format_evaluation_summary({"criteria": [row], "overall": 0.0})
    assert only.startswith("Automated evaluation summary") and "Decision 1" in only


def test_a_move_that_would_leave_one_candidate_is_rejected():
    other = _dim("2", "Locking", [_v("2.1", "Per-repo lock", accepted=["s05_p01"]), _v("2.2", "Global lock", accepted=["s06_p01"])])
    move = ExclusivityRepairOutput(rationale="x", actions=[_act("move", ["1.1", "1.2"], to="2")])   # leaves 1.3 alone
    keep = ExclusivityRepairOutput(rationale="x", actions=[])
    out, log = asyncio.run(repair_exclusivity([_commit(), other], SequenceModel([move, keep]), "Git", {}))
    assert "would keep one candidate decision (1.3 'Majority vote')" in log["rejected"][0]["message"]
    assert [v["id"] for v in out[0]["values"]] == ["1.1", "1.2", "1.3", "1.4"]


def test_single_candidate_dimensions_do_not_count():
    single = _dim("5", "Lonely", [_v("5.1", "Only option", accepted=["s01_p01", "s02_p01"])])
    assert ex.taxonomy_exclusivity([single])["score"] is None
    assert ex.taxonomy_exclusivity([_commit(), single])["score"] == pytest.approx(1 / 3)
