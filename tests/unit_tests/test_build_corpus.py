"""Passage segmentation and cleaning in benchmark/build_corpus.py, and id-preserving corpus loading."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("build_corpus", ROOT / "benchmark" / "build_corpus.py")
build_corpus = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_corpus)


def _para(n_words: int, word: str = "word") -> str:
    """A one-sentence paragraph of exactly ``n_words`` words."""
    return " ".join([word] * (n_words - 1) + [word + "."])


def test_clean_strips_links_images_urls_and_empty_bullets():
    text = "See [the docs](https://x.org/a) ![img](i.png) at https://y.org now.\n-\n42\nKeep this."
    cleaned = build_corpus.clean(text)
    assert "the docs" in cleaned and "https" not in cleaned and "img" not in cleaned
    assert "\n-\n" not in cleaned and "\n42\n" not in cleaned
    assert cleaned.endswith("Keep this.")


def test_clean_normalizes_ligatures_and_reflows_pdf_text():
    cleaned = build_corpus.clean("It is diﬃcult\nto deploy\nmodels.\n\n● point one\n● point two", from_pdf=True)
    assert "difficult to deploy models." in cleaned
    assert "● point one\n● point two" in cleaned


def test_segment_respects_target_and_min_sizes():
    text = "\n\n".join(_para(120) for _ in range(10))  # 1,200 words
    passages = build_corpus.segment(text, target=300, min_words=80, max_words=450)
    sizes = [build_corpus.words(p) for _, p in passages]
    assert sum(sizes) == 1200
    assert all(80 <= s <= 450 for s in sizes)


def test_segment_never_splits_a_code_block_and_tracks_sections():
    code = "```\n" + "\n".join(f"line {i} x y z" for i in range(40)) + "\n```"
    text = "# Intro\n\n" + _para(200) + "\n\n## Setup\n\n" + code + "\n\n" + _para(200)
    passages = build_corpus.segment(text, target=300, min_words=80, max_words=450)
    joined = [p for _, p in passages if "```" in p]
    assert len(joined) == 1 and joined[0].count("```") == 2
    assert passages[0][0] == "Intro"
    assert any(section == "Setup" for section, _ in passages)


def test_segment_splits_long_lists_by_line():
    glossary = "\n".join(f"- Term {i} — " + _para(20) for i in range(40))  # one ~880-word block
    passages = build_corpus.segment(glossary, target=300, min_words=80, max_words=450)
    assert len(passages) >= 2
    assert all(build_corpus.words(p) <= 450 for _, p in passages)


def test_merge_short_folds_tiny_passages_into_neighbours():
    merged = build_corpus.merge_short([("a", _para(200)), ("b", _para(20)), ("c", _para(300))], 80)
    assert len(merged) == 2
    assert build_corpus.words(merged[0][1]) == 220


def test_load_corpus_documents_keeps_ids(tmp_path):
    main = pytest.importorskip("main")
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps([{"id": "s01_p01", "content": "a", "title": "t"},
                                {"id": "s01_p02", "content": "b"}]))
    docs = main.load_corpus_documents(str(path))
    assert [d.id for d in docs] == ["s01_p01", "s01_p02"]
    assert [d.content for d in docs] == ["a", "b"]


def test_load_corpus_documents_rejects_duplicate_ids_and_falls_back_for_strings(tmp_path):
    main = pytest.importorskip("main")
    dup = tmp_path / "dup.json"
    dup.write_text(json.dumps([{"id": "x", "content": "a"}, {"id": "x", "content": "b"}]))
    with pytest.raises(ValueError, match="duplicate"):
        main.load_corpus_documents(str(dup))

    plain = tmp_path / "plain.json"
    plain.write_text(json.dumps(["first doc", "second doc"]))
    docs = main.load_corpus_documents(str(plain))
    assert [d.content for d in docs] == ["first doc", "second doc"]
    assert len({d.id for d in docs}) == 2
