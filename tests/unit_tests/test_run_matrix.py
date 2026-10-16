"""benchmark/run_matrix.py: the evaluation rows, their config copies and the run log."""

import csv
import importlib.util
import sys
from pathlib import Path

import yaml

from taxonomy_generator.settings import load_settings

spec = importlib.util.spec_from_file_location(
    "run_matrix_cli", Path(__file__).resolve().parents[2] / "benchmark" / "run_matrix.py")
rm = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rm                     # dataclasses look their module up while the class is built
spec.loader.exec_module(rm)


def test_matrix_rows_point_at_existing_configs_and_corpora():
    assert {"S1", "S2", "S3", "M1", "M9", "B12", "A8"} <= set(rm.MATRIX)
    for row in rm.MATRIX.values():
        assert row.config.exists(), row.id
        if not row.baseline:
            assert row.corpus.exists(), row.id
    assert [r.seed for r in rm.MATRIX.values() if r.case == "c3-git-at-scale" and r.variant == "full"] == [42, 43, 44]


def test_config_copy_sets_seed_name_and_overrides(tmp_path, monkeypatch):
    monkeypatch.setattr(rm, "OUT", tmp_path)
    path = rm.write_config(rm.MATRIX["S2"])
    data = yaml.safe_load(path.read_text())
    assert data["pipeline"]["random_seed"] == 42
    assert data["taxonomy"]["name"] == "c3-git-at-scale-sample-nofeedback-s42"
    assert data["taxonomy"]["max_num_clusters"] == 8                      # the rest of the sample config is kept
    settings = load_settings(str(path))
    assert settings.evaluation.loop_feedback is False


def test_failed_step_is_retried_once_then_recorded_and_stops(tmp_path, monkeypatch):
    monkeypatch.setattr(rm, "OUT", tmp_path)
    monkeypatch.setattr(rm, "LOG", tmp_path / "runs.csv")
    calls = []
    monkeypatch.setattr(rm, "commands", lambda row, config: [[sys.executable, "-c", "import sys; sys.exit(3)"]])
    monkeypatch.setattr(rm.subprocess, "call", lambda cmd, **kw: calls.append(cmd) or 3)
    assert rm.main(["S1", "S3"]) == 1
    assert len(calls) == 2                                                 # one retry, and S3 never ran
    [entry] = list(csv.DictReader((tmp_path / "runs.csv").open()))
    assert entry["row"] == "S1" and entry["status"] == "failed-run" and entry["attempts"] == "2"
