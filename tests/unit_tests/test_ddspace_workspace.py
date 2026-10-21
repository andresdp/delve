"""ddspace init, sources and corpus: workspace layout, ddspace.yaml, text extraction and passages."""

import csv
import json
import stat
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from delvedspace import cli
from delvedspace import extract as ex
from delvedspace import sources as src
from delvedspace.corpus import passages_for_source
from delvedspace.workspace import (
    Settings,
    Workspace,
    WorkspaceError,
    render_config,
    set_value,
)
from taxonomy_generator.settings import load_settings

ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()


def _invoke(*args, input=None):
    return runner.invoke(cli.app, list(args), input=input)


def _para(n: int, word: str = "design") -> str:
    return " ".join([word] * (n - 1) + [word + "."])


def _pdf(text: str) -> bytes:
    """A one-page PDF whose text layer holds ``text`` (correct xref offsets)."""
    words = text.split()
    lines = [" ".join(words[i:i + 6]) for i in range(0, len(words), 6)]
    stream = ("BT /F1 12 Tf 14 TL 72 720 Td " + " ".join(f"({line}) Tj T*" for line in lines) + " ET").encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(out)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A fresh workspace created with ``init --yes``; the current folder is its root."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    root = tmp_path / "space"
    result = _invoke("init", str(root), "--yes", "--max-dimensions", "5", "--use-case", "Git hosting at scale")
    assert result.exit_code == 0, result.output
    monkeypatch.chdir(root)
    return Workspace(root)


# ---------------------------------------------------------------- init and ddspace.yaml


def test_init_yes_writes_a_config_the_pipeline_loads(ws):
    assert (ws.root / "sources").is_dir() and (ws.root / "runs").is_dir()
    assert "corpus.json" in (ws.root / ".gitignore").read_text()
    settings = load_settings(str(ws.config_path))
    assert settings.taxonomy.max_num_clusters == 5
    assert settings.taxonomy.use_case == "Git hosting at scale"
    assert settings.taxonomy.name == "space"
    assert settings.models.generation_llm == "openai/gpt-5.6-luna"
    assert settings.output.default_output_dir == "runs"
    cfg = ws.config()
    assert cfg["workspace"] == {"sources_dir": "sources", "current_run": None}
    assert cfg["wiki"]["html_report"] is False and cfg["wiki"]["quotes"] is None


def test_init_refuses_an_existing_workspace_unless_forced(ws):
    assert _invoke("init", str(ws.root), "--yes").exit_code == 1
    result = _invoke("init", str(ws.root), "--yes", "--force", "--no-critic", "--max-dimensions", "0")
    assert result.exit_code == 0, result.output
    assert ws.config()["evaluation"]["enabled"] is False
    assert ws.config()["taxonomy"]["max_num_clusters"] is None


def _key_paths(d, prefix=""):
    for k, v in d.items():
        yield prefix + k
        if isinstance(v, dict):
            yield from _key_paths(v, prefix + k + ".")


def test_template_covers_every_pipeline_setting():
    template = yaml.safe_load(render_config(Settings(name="x", use_case="y")))
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    missing = set(_key_paths(config)) - set(_key_paths(template))
    assert not missing, f"ddspace.yaml template lacks settings added to config.yaml: {sorted(missing)}"


def test_use_case_with_quotes_and_colons_round_trips():
    tricky = 'Teams: "monorepo" vs. polyrepo; 100% of #choices'
    assert yaml.safe_load(render_config(Settings(name="n", use_case=tricky)))["taxonomy"]["use_case"] == tricky


def test_interactive_init_applies_answers_and_writes_the_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(cli, "interactive", lambda yes: not yes)
    answers = "\n".join([
        "my space",                      # name
        "Replication design for Git",    # use case
        "", "", "",                      # models: defaults
        "docs",                          # sources folder
        "abc",                           # invalid max dimensions -> asked again
        "7",                             # max dimensions
        "5",                             # batch size
        "n",                             # critic off
        "y",                             # write the API key
        "sk-test",                       # the key
    ]) + "\n"
    result = _invoke("init", str(tmp_path / "w"), input=answers)
    assert result.exit_code == 0, result.output
    w = Workspace(tmp_path / "w")
    cfg = w.config()
    assert cfg["taxonomy"]["name"] == "my space" and cfg["taxonomy"]["max_num_clusters"] == 7
    assert cfg["pipeline"]["batch_size"] == 5 and cfg["evaluation"]["enabled"] is False
    assert cfg["workspace"]["sources_dir"] == "docs" and (w.root / "docs").is_dir()
    assert "OPENAI_API_KEY=sk-test" in w.env_path.read_text()
    assert stat.S_IMODE(w.env_path.stat().st_mode) == 0o600
    assert w.env_value("OPENAI_API_KEY") == "sk-test"


def test_set_value_edits_one_key_and_keeps_comments():
    text = render_config(Settings(name="x", use_case="y"))
    out = set_value(text, "workspace.current_run", "runs/20261013_120000")
    assert yaml.safe_load(out)["workspace"]["current_run"] == "runs/20261013_120000"
    assert out.count("\n#") == text.count("\n#") and len(out.splitlines()) == len(text.splitlines())
    # the same key name in another block is left alone
    out = set_value(text, "evaluation.enabled", False)
    cfg = yaml.safe_load(out)
    assert cfg["evaluation"]["enabled"] is False and cfg["visualization"]["enabled"] is False
    out = set_value(text, "visualization.enabled", True)
    assert yaml.safe_load(out)["evaluation"]["enabled"] is True
    with pytest.raises(WorkspaceError):
        set_value(text, "workspace.nope", 1)


def test_commands_outside_a_workspace_explain_what_to_do(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for command in ("sources", "corpus"):
        result = _invoke(command)
        assert result.exit_code == 1 and "ddspace init" in result.output


def test_workspace_is_found_from_a_subfolder(ws):
    assert Workspace.find(ws.root / "sources").root == ws.root


# ---------------------------------------------------------------- sources


def _write_sources(folder: Path):
    (folder / "notes.md").write_text("# Replica placement\n\n" + _para(400) + "\n\n## References\n\n- a paper\n")
    (folder / "plain.txt").write_text(_para(350, "repository"))
    (folder / "page.html").write_text(
        '<html><head><title>Spokes &amp; replicas</title>'
        '<link rel="canonical" href="https://example.org/spokes"></head>'
        f"<body><article><h1>Spokes</h1><p>{_para(400, 'replica')}</p></article></body></html>")
    (folder / "paper.pdf").write_bytes(_pdf(" ".join(["consensus"] * 40)))
    (folder / "scan.pdf").write_bytes(_pdf(""))
    (folder / "image.png").write_bytes(b"\x89PNG")          # unsupported: ignored
    (folder / ".hidden.md").write_text("ignored")


def test_sources_extracts_every_format_and_drafts_sources_csv(ws):
    _write_sources(ws.sources_dir)
    result = _invoke("sources")
    assert result.exit_code == 0, result.output
    found = {s.file: s for s in src.load_manifest(ws)}
    assert set(found) == {"notes.md", "page.html", "paper.pdf", "plain.txt", "scan.pdf"}
    assert [s.id for s in src.load_manifest(ws)] == ["s1", "s2", "s3", "s4", "s5"]  # sorted by file name
    page = found["page.html"]
    assert page.title == "Spokes & replicas" and page.url == "https://example.org/spokes"
    assert found["notes.md"].title == "Replica placement"
    assert "a paper" not in (ws.text_dir / f"{found['notes.md'].id}.md").read_text()  # references trimmed
    assert found["paper.pdf"].words >= 40 and src.usable(found["paper.pdf"])
    assert found["scan.pdf"].flags == ["no_text_layer"] and not src.usable(found["scan.pdf"])
    assert "short" in found["paper.pdf"].flags
    assert "OCR" in result.output
    rows = list(csv.DictReader(open(ws.sources_csv)))
    assert [r["file"] for r in rows] == sorted(found)
    assert list(rows[0]) == src.CSV_COLUMNS


def test_rescan_keeps_ids_and_edits_appends_new_files_and_flags_missing_ones(ws):
    _write_sources(ws.sources_dir)
    src.scan(ws)
    rows = src.read_csv(ws.sources_csv)
    for row in rows:
        if row["file"] == "plain.txt":
            row.update(title="My title", source_type="blog", priority="high")  # user edits + extra column
    src.write_csv(ws.sources_csv, rows)
    (ws.sources_dir / "notes.md").unlink()
    (ws.sources_dir / "a-new-one.md").write_text(_para(320))
    found = {s.file: s for s in src.scan(ws)}
    assert found["a-new-one.md"].id == "s6"                   # next id, even though it sorts first
    assert found["notes.md"].flags == ["missing"] and found["notes.md"].id == "s1"
    rows = {r["file"]: r for r in src.read_csv(ws.sources_csv)}
    assert rows["plain.txt"]["title"] == "My title" and rows["plain.txt"]["priority"] == "high"
    assert found["plain.txt"].title == "My title"


def test_pdf_falls_back_to_pypdf_without_pdftotext(tmp_path, monkeypatch):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(_pdf("Quorum writes need three replicas"))
    monkeypatch.setattr(ex.shutil, "which", lambda name: None)
    assert "Quorum writes need three replicas" in ex.extract_pdf(pdf)


# ---------------------------------------------------------------- corpus


def test_corpus_needs_a_scan_first(ws):
    result = _invoke("corpus")
    assert result.exit_code == 1 and "ddspace sources" in result.output


def test_corpus_splits_usable_sources_into_passages(ws):
    _write_sources(ws.sources_dir)
    src.scan(ws)
    result = _invoke("corpus")
    assert result.exit_code == 0, result.output
    corpus = json.loads(ws.corpus_path.read_text())
    by_source = {}
    for p in corpus:
        by_source.setdefault(p["source_id"], []).append(p)
    manifest = {s.id: s for s in src.load_manifest(ws)}
    assert set(by_source) == {i for i, s in manifest.items() if src.usable(s)}
    for sid, passages in by_source.items():
        expected = passages_for_source(sid, (ws.text_dir / f"{sid}.md").read_text(), manifest[sid].title,
                                       manifest[sid].url, from_pdf=manifest[sid].format == "pdf")
        assert passages == expected
        assert all(p["id"].startswith(f"s{int(sid[1:]):02d}_p") for p in passages)  # s1 -> s01_p01, s01_p02, ...
    assert {"id", "content", "source_id", "title", "section", "url", "words"} <= set(corpus[0])


def test_workspace_defaults_code_the_passage_text_without_summaries(ws):
    settings = load_settings(str(ws.config_path))
    assert settings.summarization.skip is True and settings.open_coding.input == "content"


def test_unreadable_pdf_is_flagged_and_does_not_abort_the_scan(ws):
    (ws.sources_dir / "broken.pdf").write_bytes(b"\x00\x01 not a pdf " * 50)
    (ws.sources_dir / "notes.md").write_text("# Replica placement\n\n" + _para(400))
    found = {s.file: s for s in src.scan(ws)}
    assert found["broken.pdf"].flags == ["unreadable"] and found["broken.pdf"].error
    assert not src.usable(found["broken.pdf"]) and found["broken.pdf"].words == 0
    assert src.usable(found["notes.md"]) and "unreadable" in src.FLAG_HELP


def test_failed_pdftotext_falls_back_to_pypdf(tmp_path, monkeypatch):
    path = tmp_path / "paper.pdf"
    path.write_bytes(_pdf(" ".join(["consensus"] * 40)))
    monkeypatch.setattr(ex.shutil, "which", lambda name: "/usr/bin/pdftotext")
    monkeypatch.setattr(ex.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 1, "stdout": ""})())
    assert "consensus" in ex.extract_pdf(path)


def test_init_rejects_an_embedding_provider_the_pipeline_cannot_load(tmp_path):
    result = _invoke("init", str(tmp_path / "w"), "--yes", "--embedding", "anthropic/some-model")
    assert result.exit_code == 1 and "openai/" in result.output
    assert not (tmp_path / "w" / "ddspace.yaml").exists()


def test_default_embeddings_are_openai(ws):
    assert ws.config()["models"]["embedding"] == "openai/text-embedding-3-small"


def test_init_from_config_takes_the_use_case_models_and_size(tmp_path):
    cfg = tmp_path / "example.yaml"
    cfg.write_text("models:\n  generation_llm: openai/gpt-x\n  embedding: openai/text-embedding-3-large\n"
                   "pipeline:\n  batch_size: 8\ntaxonomy:\n  max_num_clusters: 7\n  use_case: >-\n"
                   "    Classify bike-sharing\n    decisions.\nevaluation:\n  enabled: false\n")
    result = _invoke("init", str(tmp_path / "w"), "--yes", "--from-config", str(cfg))
    assert result.exit_code == 0, result.output
    c = Workspace(tmp_path / "w").config()
    assert c["taxonomy"]["use_case"] == "Classify bike-sharing decisions."
    assert c["taxonomy"]["max_num_clusters"] == 7 and c["pipeline"]["batch_size"] == 8
    assert c["models"]["generation_llm"] == "openai/gpt-x" and c["evaluation"]["enabled"] is False
    assert c["models"]["embedding"] == "openai/text-embedding-3-large"


def test_init_from_a_missing_config_explains(tmp_path):
    result = _invoke("init", str(tmp_path / "w"), "--yes", "--from-config", str(tmp_path / "nope.yaml"))
    assert result.exit_code == 1 and "Cannot read" in result.output


@pytest.mark.parametrize("data", [
    ["Use an API gateway. It routes requests.", "Store events in Kafka."],
    [{"content": "Use an API gateway. It routes requests."}, {"content": "Store events in Kafka.", "title": "Kafka"}],
    {"taxonomy_name": "x", "documents": [{"id": "u1", "content": "Use an API gateway. It routes requests."},
                                         {"id": "u2", "content": "Store events in Kafka."}]},
])
def test_sources_from_json_writes_one_file_per_document(ws, data):
    corpus = ws.root / "decisions.json"
    corpus.write_text(json.dumps(data))
    result = _invoke("sources", "--from-json", str(corpus))
    assert result.exit_code == 0, result.output
    found = src.load_manifest(ws)
    assert [s.file for s in found] == ["decisions-01.md", "decisions-02.md"]
    assert found[0].title == "Use an API gateway" and all(src.usable(s) for s in found)
    assert _invoke("sources", "--from-json", str(corpus)).exit_code == 0     # importing again adds nothing
    assert len(src.load_manifest(ws)) == 2


def test_sources_from_bad_json_explains(ws):
    bad = ws.root / "bad.json"
    bad.write_text('{"documents": []}')
    result = _invoke("sources", "--from-json", str(bad))
    assert result.exit_code == 1 and "Cannot import" in result.output


def test_sources_builds_the_corpus_unless_told_not_to(ws):
    _write_sources(ws.sources_dir)
    result = _invoke("sources", "--no-corpus")
    assert result.exit_code == 0 and not ws.corpus_path.exists() and "ddspace corpus" in result.output
    result = _invoke("sources")
    assert result.exit_code == 0 and ws.corpus_path.is_file() and "ddspace mine" in result.output
    assert json.loads(ws.corpus_path.read_text())


def test_secrets_show_only_their_first_characters():
    from delvedspace import ui
    assert ui.mask_secret("sk-proj-abcdefghij") == "sk-proj-" + "•" * 10
    assert ui.mask_secret("short") == "short"


def test_found_api_key_is_shown_masked(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-SECRETSECRET")
    result = _invoke("init", str(tmp_path / "w"), "--yes")
    assert "sk-proj-" in result.output and "SECRETSECRET" not in result.output
