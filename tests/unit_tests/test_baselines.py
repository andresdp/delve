"""benchmark/baselines.py: long-context (L1) and prior-knowledge (L5) baselines, written as run files."""

import importlib.util
import json
from pathlib import Path

import pytest

from taxonomy_generator.schemas import Cluster, TaxonomyOutput, Value
from taxonomy_generator.utils import load_seed_taxonomy

spec = importlib.util.spec_from_file_location(
    "baselines_cli", Path(__file__).resolve().parents[2] / "benchmark" / "baselines.py")
bl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bl)

CORPUS = [{"id": "s01_p01", "content": "Spokes keeps three replicas."},
          {"id": "s02_p01", "content": "DRBD was rejected for replication."}]


def _output():
    values = [Value(id="1.1", dimension_id="1", label="Three replicas", description="",
                    supporting_doc_ids=["s01_p01", "s99_p99"], status="accepted"),
              Value(id="1.1", dimension_id="1", label="DRBD", description="",          # duplicate id on purpose
                    supporting_doc_ids=["s02_p01"], status="rejected")]
    return TaxonomyOutput(clusters=[Cluster(id="1", name="Replication", description="How?", values=values)],
                          explanation="One decision point.")


def test_long_context_prompt_carries_every_passage_and_prior_knowledge_none():
    l1 = bl.build_prompt("long_context", "Git at scale.", CORPUS)
    assert "[s01_p01] Spokes keeps three replicas." in l1 and "[s02_p01]" in l1 and "Git at scale." in l1
    l5 = bl.build_prompt("prior_knowledge", "Git at scale.", None)
    assert "s01_p01" not in l5 and "no sources" in l5 and "Git at scale." in l5


def test_run_file_has_unique_ids_known_evidence_and_loads_as_a_seed(tmp_path):
    run = bl.to_run(_output(), case="c1-ml-workflow", kind="long_context", seed=42, model="openai/x", prompt="p",
                    prompt_tokens=10, known_ids={"s01_p01", "s02_p01"}, usage={"total_tokens": 5}, elapsed=1.0)
    values = run["selected_clusters"][0]["values"]
    assert [v["id"] for v in values] == ["1.1", "1.2"]
    assert values[0]["supporting_doc_ids"] == ["s01_p01"] and run["baseline"]["unknown_passage_ids_dropped"] == 1
    assert run["mode"] == "baseline-l1" and run["iterations"][0]["clusters"] == run["selected_clusters"]
    path = tmp_path / "c1-ml-workflow-baseline-l1_taxonomy_20261016_000000.json"
    path.write_text(json.dumps(run))
    assert load_seed_taxonomy(str(path), "selected")[0]["name"] == "Replication"


def test_prior_knowledge_keeps_no_evidence():
    run = bl.to_run(_output(), case="c2-rl-monitoring", kind="prior_knowledge", seed=43, model="openai/x",
                    prompt="p", prompt_tokens=10, known_ids=None, usage={}, elapsed=0.0)
    assert all(not v["supporting_doc_ids"] for v in run["selected_clusters"][0]["values"])
    assert run["taxonomy_name"] == "c2-rl-monitoring-baseline-l5"


def test_cli_writes_a_run_without_truncating(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps(CORPUS))

    async def fake_call(model, prompt):
        return _output(), {"total_tokens": 7, "prompt_tokens": 5, "completion_tokens": 2}

    monkeypatch.setattr(bl, "call", fake_call)
    out = tmp_path / "out"
    assert bl.main(["--case", "c1-ml-workflow", "--kind", "long_context", "--corpus", str(corpus),
                    "--out", str(out)]) == 0
    [written] = list(out.glob("c1-ml-workflow-baseline-l1_taxonomy_*.json"))
    data = json.loads(written.read_text())
    assert data["run_metrics"]["total_tokens"] == 7 and data["baseline"]["prompt_tokens_counted"] > 0
    assert bl.main(["--case", "c1-ml-workflow", "--kind", "long_context", "--corpus", str(corpus),
                    "--max-input-tokens", "10", "--out", str(out)]) == 2      # too large: stop, never truncate
