"""ddspace point: a design point from chosen values, checked without an LLM; described from the wiki or on the fly."""

import json
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from delvedspace import cli
from delvedspace import point as pt
from taxonomy_generator.wiki import build, write
from taxonomy_generator.wiki import query as q
from tests.unit_tests.test_wiki_export import POINTS, _inputs

runner = CliRunner()
STORED = "Disk quorum with three-phase commit. Trade-off: durable on a node failure, at the cost of write latency."
OLD_STORED = "Disk quorum with three-phase commit."   # stored before descriptions named their trade-off


class FakeModel:
    """Counts calls; returns a fixed description."""

    def __init__(self):
        self.prompts = []

    async def ainvoke(self, prompt):
        self.prompts.append(prompt)
        return SimpleNamespace(content="A WAL in S3 with a shared label.")


class NoCalls:
    async def ainvoke(self, prompt):
        raise AssertionError("no LLM call expected")


@pytest.fixture
def root(tmp_path, monkeypatch):
    """An export whose design point P001 (Disk quorum + Three-phase commit) has a stored description."""
    root = tmp_path / "space"
    write(build(_inputs(design_points=POINTS, point_descriptions={"1=1.1|2=2.1": STORED})), root, "toy")
    monkeypatch.chdir(root)
    return root


def _files(root):
    return {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}


def test_an_existing_point_returns_its_stored_description_without_a_call(root):
    info = pt.point(root / "raw" / "graph.json", ["Disk quorum", "Three-phase commit"], model=NoCalls())
    assert info["existing"]["id"] == "p:P001" and info["existing"]["group"] == "attested"
    assert info["description"] == STORED and info["description_source"] == "stored"
    assert [s["id"] for s in info["attested_by"]] == ["s:s1"] and info["warnings"] == []
    assert [r["type"] for r in info["relations"]] == ["constrains"]


def test_a_stored_description_without_its_trade_off_is_described_again(tmp_path, monkeypatch):
    root = tmp_path / "old"
    write(build(_inputs(design_points=POINTS, point_descriptions={"1=1.1|2=2.1": OLD_STORED})), root, "toy")
    model = FakeModel()
    info = pt.point(root / "raw" / "graph.json", ["Disk quorum", "Three-phase commit"], model=model)
    assert info["description_source"] == "generated" and len(model.prompts) == 1
    assert pt.point(root / "raw" / "graph.json", ["Disk quorum", "Three-phase commit"], llm=False)["description"] \
        == OLD_STORED                                            # without an LLM, the stored text is all there is


def test_the_prompt_asks_for_the_trade_off(root):
    model = FakeModel()
    pt.point(root / "raw" / "graph.json", ["WAL in S3"], model=model)
    assert "Trade-off:" in model.prompts[0] and "mined from engineering documents" in model.prompts[0]


def test_a_named_point_is_described_without_a_space(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)                                   # no workspace anywhere
    model = FakeModel()
    info = pt.named_point(["Storage:  Local disks", "Replication: Quorum"], domain="a KV store", model=model)
    assert [v["id"] for v in info["values"]] == ["Storage: Local disks", "Replication: Quorum"]
    assert info["space"] is None and info["description_source"] == "generated" and info["note"] == pt.NAMED_NOTE
    prompt = model.prompts[0]
    assert "without a design space" in prompt and "a KV store" in prompt and "Value: Local disks" in prompt
    assert "None" not in prompt and "[status" not in prompt
    with pytest.raises(q.QueryError, match="second value"):
        pt.named_point(["Storage: Local disks", "Storage: S3"], model=model)
    with pytest.raises(q.QueryError, match="Dimension: Value"):
        pt.named_point(["Local disks"], model=model)


def test_cli_no_space_needs_a_model_and_checks_names(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(pt.MODEL_ENV, raising=False)
    result = runner.invoke(cli.app, ["point", "--no-space", "Storage: Local disks"])
    assert result.exit_code != 0 and pt.MODEL_ENV in " ".join(result.output.split())
    result = runner.invoke(cli.app, ["point", "--no-space", "--no-llm", "Storage: Local disks", "Replication: Quorum"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["description"] is None and len(data["values"]) == 2
    result = runner.invoke(cli.app, ["point", "--no-space", "--no-llm", "Local disks"])
    assert result.exit_code != 0


def test_a_new_point_is_generated_once_and_nothing_is_written(root):
    before = _files(root)
    model = FakeModel()
    info = pt.point(root / "raw" / "graph.json", ["WAL in S3", "Replication=Shared label"], model=model)
    assert info["existing"] is None and info["description_source"] == "generated"
    assert info["description"] == "A WAL in S3 with a shared label." and info["note"] == pt.GENERATED_NOTE
    assert len(model.prompts) == 1 and "WAL in S3" in model.prompts[0] and "Shared label" in model.prompts[0]
    assert [s["id"] for s in info["attested_by"]] == ["s:s2"]   # accepts WAL in S3, supports Shared label
    assert _files(root) == before                               # no file created or changed


def test_ambiguous_label_needs_the_dimension(root):
    graph = q.load(root / "raw" / "graph.json")
    with pytest.raises(q.NotFound) as exc:
        q.point(graph, ["Shared label"])
    assert {c["id"] for c in exc.value.candidates} == {"v:1.3", "v:2.2"}
    info = q.point(graph, ["Source of truth=Shared label"])
    assert info["values"][0]["id"] == "v:1.3" and "rejected" in info["warnings"][0]


def test_warnings_for_two_values_of_one_dimension_and_an_outcome(root):
    info = q.point(q.load(root / "raw" / "graph.json"), ["Disk quorum", "WAL in S3", "Lower latency"])
    text = " ".join(info["warnings"])
    assert "2 values of 'Source of truth'" in text and "'Lower latency' is an outcome" in text
    assert info["attested_by"] == []


def test_cli_checks_only_with_no_llm_and_exits_2_on_unknown_names(root):
    g = ["--graph", str(root)]
    result = runner.invoke(cli.app, ["point", "Disk quorum", "Three-phase commit", "--no-llm", *g])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["description"] == STORED     # stored text needs no LLM
    result = runner.invoke(cli.app, ["point", "WAL in S3", "--no-llm", *g])
    assert json.loads(result.output)["description"] is None
    result = runner.invoke(cli.app, ["point", "Disk quorom", "--no-llm", *g])
    assert result.exit_code == 2


def test_cli_without_a_recorded_model_asks_for_one(root):
    result = runner.invoke(cli.app, ["point", "WAL in S3", "--graph", str(root)])
    assert result.exit_code == 1 and "--model" in result.output


@pytest.mark.parametrize("name", ["three-phase commit", "THREE PHASE COMMIT", "three_phase  commit",
                                  "replication=three phase commit"])
def test_names_match_ignoring_case_spacing_and_punctuation(root, name):
    info = q.point(q.load(root / "raw" / "graph.json"), [name])
    assert info["values"][0]["id"] == "v:2.1"
