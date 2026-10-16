#!/usr/bin/env python3
"""Build Delve corpora (one passage per document) from downloaded ADD-Bench sources.

Reads ``benchmark/<case>/sources/text/sNN.md`` (produced by ``fetch_sources.py``),
strips the provenance header and markdown noise, splits every source into
passages of roughly ``--target-words`` words at paragraph/heading boundaries
(never inside a fenced code block), and writes:

- ``examples/<case>/<case>_corpus.json``: Delve corpus, a JSON array of
  ``{"id", "content", "source_id", "title", "section", "url", "words"}``. Delve's
  loader uses ``id`` and ``content`` and ignores the rest. Passage ids have the
  form ``s03_p02`` (source 3, passage 2), so every open code and value keeps its
  provenance.
- ``examples/<case>/<case>_passages.csv``: the same index without the text
  (id, source_id, section, words), safe to version-control.

Sources whose manifest entry has no usable text (status ``failed`` or 0 words)
are skipped and reported.

Usage::

    python benchmark/build_corpus.py                    # C1 and C2
    python benchmark/build_corpus.py c2-rl-monitoring --target-words 250

The corpus contains third-party text: it is gitignored in the example folders.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict

from delvedspace.corpus import (  # noqa: F401  (moved into the package; re-exported here)
    blocks, clean, merge_short, reflow, segment, split_long, words,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_CASES = ["c1-ml-workflow", "c2-rl-monitoring"]


def body(md: str) -> str:
    """Drop the provenance header written by fetch_sources.py."""
    return md.split("\n---\n", 1)[1] if "\n---\n" in md else md


def build_case(case: str, target: int, min_words: int, max_words: int, out_root: Path) -> Dict:
    case_dir = HERE / case
    rows = {r["id"]: r for r in csv.DictReader(open(case_dir / "sources.csv", encoding="utf-8"))}
    manifest = {e["id"]: e for e in json.loads((case_dir / "sources" / "manifest.json").read_text())}

    corpus, skipped = [], []
    for sid in sorted(rows, key=lambda s: int(s[1:])):
        entry, text_file = manifest.get(sid, {}), case_dir / "sources" / "text" / f"{sid}.md"
        if entry.get("status") == "failed" or not entry.get("words") or not text_file.exists():
            skipped.append(sid)
            continue
        from_pdf = str(entry.get("raw_file", "")).endswith(".pdf")
        text = clean(body(text_file.read_text(encoding="utf-8")), from_pdf=from_pdf)
        n = int(sid[1:])
        for k, (section, passage) in enumerate(segment(text, target, min_words, max_words), start=1):
            corpus.append({
                "id": f"s{n:02d}_p{k:02d}",
                "content": passage,
                "source_id": sid,
                "title": rows[sid]["title"],
                "section": section,
                "url": rows[sid]["url"],
                "words": words(passage),
            })

    out_dir = out_root / case
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{case}_corpus.json").write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(out_dir / f"{case}_passages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "source_id", "section", "words"], extrasaction="ignore")
        w.writeheader()
        w.writerows(corpus)

    sizes = sorted(p["words"] for p in corpus)
    return {
        "case": case, "sources": len({p["source_id"] for p in corpus}), "skipped": skipped,
        "passages": len(corpus), "words": sum(sizes),
        "min": sizes[0] if sizes else 0, "median": sizes[len(sizes) // 2] if sizes else 0,
        "max": sizes[-1] if sizes else 0, "out": str(out_dir / f"{case}_corpus.json"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="*", default=DEFAULT_CASES, help="case folders under benchmark/")
    ap.add_argument("--target-words", type=int, default=300, help="passage size to aim for")
    ap.add_argument("--min-words", type=int, default=80, help="shorter tails are merged into the previous passage")
    ap.add_argument("--max-words", type=int, default=450, help="hard cap before a passage is closed")
    ap.add_argument("--out-root", type=Path, default=REPO / "examples", help="where <case>/ corpus folders go")
    args = ap.parse_args()

    for case in args.cases:
        s = build_case(case, args.target_words, args.min_words, args.max_words, args.out_root)
        print(f"{s['case']}: {s['passages']} passages from {s['sources']} sources "
              f"({s['words']:,} words; min/median/max {s['min']}/{s['median']}/{s['max']}) "
              f"skipped={s['skipped'] or 'none'} -> {s['out']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
