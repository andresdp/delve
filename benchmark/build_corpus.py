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
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_CASES = ["c1-ml-workflow", "c2-rl-monitoring"]

IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]+)\]\((?:[^()\s]|\([^)]*\))*\)")
AUTOLINK = re.compile(r"<https?://[^>]+>")
BARE_URL = re.compile(r"https?://\S+")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])")


def words(text: str) -> int:
    return len(text.split())


LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}
LIST_ITEM = re.compile(r"^\s*([-*•●▪]|\d+[.)])\s+")


def reflow(text: str) -> str:
    """Join hard-wrapped lines inside paragraphs (PDF/slide text); keep list items."""
    out = []
    for block in text.split("\n\n"):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        merged: List[str] = []
        for line in lines:
            if merged and not LIST_ITEM.match(line):
                merged[-1] = merged[-1] + " " + line
            else:
                merged.append(line)
        out.append("\n".join(merged))
    return "\n\n".join(out)


def clean(text: str, from_pdf: bool = False) -> str:
    """Remove markdown noise that carries no meaning for coding."""
    for lig, repl in LIGATURES.items():
        text = text.replace(lig, repl)
    text = IMAGE.sub("", text)
    text = LINK.sub(r"\1", text)
    text = AUTOLINK.sub("", text)
    text = BARE_URL.sub("", text)
    text = text.replace("**", "").replace("__", "")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"[-*•●▪]\s*", stripped):    # empty bullet
            continue
        if re.fullmatch(r"\d{1,4}", stripped):         # stray vote/karma/page numbers
            continue
        lines.append(line.rstrip())
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return reflow(text) if from_pdf else text


def blocks(text: str) -> List[str]:
    """Split into paragraph blocks; a fenced code block is always one block."""
    out, buf, in_code = [], [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            buf.append(line)
            if not in_code:          # closing fence ends the block
                out.append("\n".join(buf)); buf = []
            continue
        if in_code:
            buf.append(line)
        elif line.strip():
            buf.append(line)
        elif buf:
            out.append("\n".join(buf)); buf = []
    if buf:
        out.append("\n".join(buf))
    return [b.strip() for b in out if b.strip()]


def _pack(units: List[str], target: int, sep: str) -> List[str]:
    parts, cur = [], []
    for u in units:
        if cur and words(sep.join(cur + [u])) > target:
            parts.append(sep.join(cur)); cur = []
        cur.append(u)
    if cur:
        parts.append(sep.join(cur))
    return parts


def split_long(block: str, target: int) -> List[str]:
    """Split an oversized block: by lines first (lists, tables), then by sentences.

    Fenced code blocks stay whole.
    """
    if block.lstrip().startswith("```"):
        return [block]
    lines = [l for l in block.splitlines() if l.strip()]
    if len(lines) > 1:
        out = []
        for part in _pack(lines, target, "\n"):
            out.extend(split_long(part, target) if words(part) > target * 1.5 and "\n" not in part else [part])
        return out
    return _pack(SENTENCE_END.split(block), target, " ")


def segment(text: str, target: int, min_words: int, max_words: int) -> List[Tuple[str, str]]:
    """Group blocks into passages of ~target words. Returns (section, passage) pairs."""
    passages: List[Tuple[str, str]] = []
    section, chunk_section, chunk = "", "", []

    def flush():
        nonlocal chunk
        if chunk:
            passages.append((chunk_section, "\n\n".join(chunk)))
            chunk = []

    for block in blocks(text):
        m = HEADING.match(block) if "\n" not in block else None
        if m:
            # Prefer breaking at a heading once the chunk has enough material
            # (half the target), so many short sections do not each become a
            # tiny passage.
            if words("\n\n".join(chunk)) >= max(min_words, target // 2):
                flush()
            section = m.group(2).strip().strip("#").strip()
        pieces = split_long(block, target) if words(block) > max_words else [block]
        for piece in pieces:
            if not chunk:
                chunk_section = section
            if chunk and words("\n\n".join(chunk + [piece])) > max_words:
                flush()
                chunk_section = section
            chunk.append(piece)
            if words("\n\n".join(chunk)) >= target:
                flush()
    flush()
    return merge_short(passages, min_words)


def merge_short(passages: List[Tuple[str, str]], min_words: int) -> List[Tuple[str, str]]:
    """Merge every passage under ``min_words`` into its smaller neighbour."""
    out = list(passages)
    i = 0
    while len(out) > 1 and i < len(out):
        if words(out[i][1]) >= min_words:
            i += 1
            continue
        prev_w = words(out[i - 1][1]) if i > 0 else None
        next_w = words(out[i + 1][1]) if i + 1 < len(out) else None
        if next_w is None or (prev_w is not None and prev_w <= next_w):
            sec, text = out[i - 1]
            out[i - 1] = (sec, text + "\n\n" + out[i][1])
            del out[i]
            i = max(i - 1, 0)
        else:
            sec, text = out[i]
            out[i] = (sec, text + "\n\n" + out[i + 1][1])
            del out[i + 1]
    return out


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
