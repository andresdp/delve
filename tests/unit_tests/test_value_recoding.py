"""Value recoding: selection, validation, application, retry, and the wiki and matcher views of the facets."""

import asyncio

from taxonomy_generator.evaluation import exclusivity as ex
from taxonomy_generator.evaluation.gt_match import system_values
from taxonomy_generator.nodes import value_recoding as vr
from taxonomy_generator.schemas import CombinationAssignment, ExclusivityRepairOutput, RecodedValue, RecodingOutput
from taxonomy_generator.wiki import build
from tests.unit_tests.test_value_exclusivity import _dim, _v
from tests.unit_tests.test_wiki_export import _inputs


def _provenance():
    """s01,s02 adopt {1.1, 1.2}; s03,s04 {1.1}; s05,s06 {1.3, 1.4}; 1.5 is only rejected."""
    return _dim("1", "ML provenance", [
        _v("1.1", "Metric recording", accepted=["s01_p01", "s02_p01", "s03_p01", "s04_p01"]),
        _v("1.2", "Metadata store", accepted=["s01_p02", "s02_p02"]),
        _v("1.3", "Lineage graph", accepted=["s05_p01", "s06_p01"]),
        _v("1.4", "Artifact versioning", accepted=["s05_p02", "s06_p02"]),
        _v("1.5", "Manual notes", rejected=["s07_p01"]),
        _v("1.6", "Auditability", accepted=["s01_p03"], status="outcome"),
    ])


def _key(dim, ids):
    return next(k for k, (vids, _u) in vr._combo_keys(dim).items() if vids == frozenset(ids))


def _proposal(dim, values=None, assign=None):
    values = values or [RecodedValue(key="A", label="Ad-hoc metric logging", description="Metrics only.", includes=["1.1"]),
                        RecodedValue(key="B", label="Experiment tracking", description="Metrics in a store.", includes=["1.1", "1.2"]),
                        RecodedValue(key="C", label="Full lineage", description="Lineage and versions.", includes=["1.3", "1.4"])]
    assign = assign or {("1.1",): "A", ("1.1", "1.2"): "B", ("1.3", "1.4"): "C"}
    return RecodingOutput(keep=False, values=values, rationale="degrees of tracking",
                          assignments=[CombinationAssignment(combination=_key(dim, ids), value_key=k) for ids, k in assign.items()])


class Model:
    def __init__(self, answers):
        self.answers, self.prompts = list(answers), []

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, messages):
        self.prompts.append("\n".join(m.content for m in messages))
        return self.answers.pop(0)


def _run(clusters, answers, **kw):
    model = Model(answers)
    out, log = asyncio.run(vr.recode_values(clusters, model, "MLOps", {"s01_p01": "We log metrics to MLflow."}, **kw))
    return out, log, model


def test_measures_combinations_recurring_share_and_generality():
    dim = _provenance()
    assert ex.recurring_share(dim) == 1.0
    assert sorted(len(u) for u in ex.value_combinations(dim).values()) == [2, 2, 2]
    assert ex.generality([dim]) == 1.0                        # every adopted value has two or more sources


def test_recoding_rewrites_values_as_alternatives_and_keeps_facets():
    dim = _provenance()
    out, log, model = _run([dim], [_proposal(dim)])
    values = {v["label"]: v for v in out[0]["values"]}
    assert set(values) == {"Ad-hoc metric logging", "Experiment tracking", "Full lineage", "Manual notes", "Auditability"}
    tracking = values["Experiment tracking"]
    assert [f["id"] for f in tracking["includes"]] == ["1.1", "1.2"]
    assert tracking["stances"]["accepted"] == ["s01_p01", "s01_p02", "s02_p01", "s02_p02"]   # only the assigned sources
    assert values["Ad-hoc metric logging"]["stances"]["accepted"] == ["s03_p01", "s04_p01"]
    assert values["Manual notes"]["status"] == "rejected" and values["Auditability"]["status"] == "outcome"
    assert log["before"] < 1 and log["after"] == 1.0 and log["fit"] == 1.0
    assert log["values_before"] == 6 and log["values_after"] == 5 and log["recoded"][0]["to"][1] == "Experiment tracking"
    assert "C1" in model.prompts[0] and "s01_p01" in model.prompts[0]
    assert dim["values"][0]["label"] == "Metric recording"                      # the input is not modified


def test_validation_rejects_bundles_gaps_and_uncovered_combinations():
    dim = _provenance()
    per_source = _proposal(dim, assign={("1.1",): "A", ("1.1", "1.2"): "B", ("1.3", "1.4"): "B"})
    assert any("does not include 1.3, 1.4" in p for p in vr.validate(dim, per_source))
    gap = _proposal(dim, values=[RecodedValue(key="A", label="x", description="", includes=["1.1", "1.2"]),
                                 RecodedValue(key="C", label="y", description="", includes=["1.3"])],
                    assign={("1.1",): "A", ("1.1", "1.2"): "A", ("1.3", "1.4"): "C"})
    problems = vr.validate(dim, gap)
    assert any("included in no new value: 1.4" in p for p in problems) and any("does not include 1.4" in p for p in problems)
    lonely = _dim("2", "D", _provenance()["values"][:4] + [_v("1.7", "Rare", accepted=["s08_p01"])])
    values = [RecodedValue(key="A", label="a", description="", includes=["1.1", "1.2"]),
              RecodedValue(key="B", label="b", description="", includes=["1.3", "1.4"]),
              RecodedValue(key="R", label="rare", description="", includes=["1.7"])]
    proposal = RecodingOutput(keep=False, values=values, rationale="", assignments=[
        CombinationAssignment(combination=k, value_key="R" if vids == {"1.7"} else "B" if "1.3" in vids else "A")
        for k, (vids, _u) in vr._combo_keys(lonely).items()])
    assert any("'rare' is adopted by 1 source(s)" in p for p in vr.validate(lonely, proposal))
    assert vr.validate(dim, RecodingOutput(keep=True, values=[], assignments=[], rationale="fine")) == []


def test_a_rejected_proposal_is_retried_with_the_problems():
    dim = _provenance()
    bad = _proposal(dim, assign={("1.1",): "A", ("1.1", "1.2"): "A", ("1.3", "1.4"): "C"})
    out, log, model = _run([dim], [bad, _proposal(dim)])
    assert len(model.prompts) == 2 and "Your previous proposal" in model.prompts[1]
    assert log["rejected"][0]["attempt"] == 1 and len(log["recoded"]) == 1


def test_keep_and_dimensions_with_unshared_combinations():
    dim = _provenance()
    out, log, _ = _run([dim], [RecodingOutput(keep=True, values=[], assignments=[], rationale="alternatives already")])
    assert log["kept"][0]["dimension_id"] == "1" and out[0]["values"][0]["label"] == "Metric recording"
    scattered = _dim("3", "Validation", [_v("3.1", "a", accepted=["s01_p01", "s02_p01", "s03_p01"]),
                                         _v("3.2", "b", accepted=["s01_p02"]), _v("3.3", "c", accepted=["s02_p02"]),
                                         _v("3.4", "d", accepted=["s03_p02"])])
    out, log, model = _run([scattered], [])
    assert log["likely_cause_ii"][0]["id"] == "3" and not log["selected"] and not model.prompts


def test_wiki_and_matcher_show_the_facets():
    dim = _provenance()
    out, log, _ = _run([dim], [_proposal(dim)])
    tax = {"taxonomy_name": "toy", "selected_clusters": out, "iterations": [{"clusters": out}],
           "operation_log": [log], "run_metrics": {}}
    export = build(_inputs(taxonomy=tax, systems={}, corpus={}))
    page = next(p for p in export.pages if p.frontmatter.get("includes") == ["Metric recording", "Metadata store"])
    assert "## Includes" in page.body
    concept = next(p for p in export.pages if p.path.startswith("concepts/"))
    assert "Values recoded as alternatives" in concept.body
    plain = {i.name: i.description for i in system_values(out)}
    faceted = {i.name: i.description for i in system_values(out, use_facets=True)}
    assert "Includes" not in plain["Experiment tracking"]
    assert faceted["Experiment tracking"].endswith("Includes: Metric recording; Metadata store.")


def test_guards_against_shared_facets_and_broad_alternatives():
    dim = _provenance()
    no_own = _proposal(dim, values=[RecodedValue(key="A", label="a", description="", includes=["1.1", "1.2", "1.3", "1.4"]),
                                    RecodedValue(key="B", label="b", description="", includes=["1.1", "1.2", "1.3", "1.4"])],
                       assign={("1.1",): "A", ("1.1", "1.2"): "A", ("1.3", "1.4"): "B"})
    assert any("include the same facets" in p for p in vr.validate(dim, no_own))
    levels = _proposal(dim)                                     # {1.1} and {1.1, 1.2} nest: allowed
    assert vr.validate(dim, levels, min_fit=0.5) == []
    broad = _proposal(dim, values=[RecodedValue(key="A", label="tracking", description="", includes=["1.1", "1.2"]),
                                   RecodedValue(key="C", label="lineage", description="", includes=["1.3", "1.4"])],
                      assign={("1.1",): "A", ("1.1", "1.2"): "A", ("1.3", "1.4"): "C"})
    assert vr.fit(dim, broad) == 2 / 3
    assert any("too broad" in p for p in vr.validate(dim, broad, min_fit=0.8))
    assert vr.validate(dim, broad, min_fit=0.5) == []


# ------------------------------------------------------------------ wiring in consolidate_values and query output


class SchemaModel:
    """A chat model stand-in: with_structured_output(schema) picks the canned answer for that schema."""

    def __init__(self, answers):
        self.answers, self.calls, self._schema = answers, [], None

    def with_structured_output(self, schema):
        bound = SchemaModel(self.answers)
        bound.calls, bound._schema = self.calls, schema
        return bound

    async def ainvoke(self, messages):
        self.calls.append(self._schema.__name__)
        return self.answers[self._schema.__name__]


def _consolidate(monkeypatch, model, **config):
    """consolidate_values on the provenance dimension, with consolidation and evidence linking stubbed out."""
    from taxonomy_generator.nodes import value_consolidator as vc
    from taxonomy_generator.state import State

    dim = _provenance()

    async def no_consolidation(state, configuration, reviewed):
        return {"clusters": [reviewed], "explanations": ["consolidated"], "status": []}

    async def linked(clusters, codes, embedding, min_similarity):
        return clusters, {"codes": 1, "assigned": 1, "unassigned": 0, "documents": 1,
                          "documents_with_evidence": 1, "linked": True}

    monkeypatch.setattr(vc, "_consolidate_values", no_consolidation)
    monkeypatch.setattr(vc, "link_evidence", linked)
    monkeypatch.setattr(vc, "load_chat_model", lambda name: model)
    state = State(clusters=[[dim]], open_codes=[{"doc_id": "s01_p01", "label": "x", "status": "accepted"}],
                  documents=[{"id": "s01_p01", "content": "We log metrics."}])
    cfg = {"configurable": {"mode": "train", "visualization_enabled": False, "merge_dimensions": False,
                            "link_evidence": True, **config}}
    return asyncio.run(vc.consolidate_values(state, cfg)), dim


def test_consolidate_values_runs_recoding_by_default_and_logs_it(monkeypatch):
    model = SchemaModel({"RecodingOutput": _proposal(_provenance())})
    result, _ = _consolidate(monkeypatch, model, exclusivity_repair=False)
    labels = {v["label"] for v in result["clusters"][0][0]["values"]}
    assert {"Ad-hoc metric logging", "Experiment tracking", "Full lineage"} <= labels
    assert [e["node"] for e in result["operation_log"]] == ["value_recoding"]
    assert "Value recoding: 1 dimension(s) selected, 1 recoded" in result["explanations"][0]
    assert model.calls == ["RecodingOutput"]


def test_consolidate_values_logs_repair_then_recoding(monkeypatch):
    model = SchemaModel({"ExclusivityRepairOutput": ExclusivityRepairOutput(actions=[], rationale="alternatives"),
                         "RecodingOutput": RecodingOutput(keep=True, values=[], assignments=[], rationale="fine")})
    result, _ = _consolidate(monkeypatch, model, exclusivity_repair=True)
    assert [e["node"] for e in result["operation_log"]] == ["exclusivity_repair", "value_recoding"]
    assert model.calls == ["ExclusivityRepairOutput", "RecodingOutput"]


def test_consolidate_values_without_recoding_calls_no_model(monkeypatch):
    model = SchemaModel({})                                   # any structured call would raise KeyError
    result, dim = _consolidate(monkeypatch, model, exclusivity_repair=False, value_recoding=False)
    assert model.calls == []
    assert [v["label"] for v in result["clusters"][0][0]["values"]] == [v["label"] for v in dim["values"]]
    assert "operation_log" not in result


def test_query_exposes_exclusivity_and_includes():
    from taxonomy_generator.wiki import query as q
    dim = _provenance()
    out, log, _ = _run([dim], [_proposal(dim)])
    tax = {"taxonomy_name": "toy", "selected_clusters": out, "iterations": [{"clusters": out}],
           "operation_log": [log], "run_metrics": {}}
    graph = build(_inputs(taxonomy=tax, systems={}, corpus={})).graph
    [d] = q.dims(graph)
    assert d["exclusivity"] == 1.0
    tracking = next(v for v in q.values(graph, d["id"])["values"] if v["label"] == "Experiment tracking")
    assert tracking["includes"] == ["Metric recording", "Metadata store"]
    plain = next(v for v in q.values(graph, d["id"])["values"] if v["label"] == "Manual notes")
    assert "includes" not in plain
