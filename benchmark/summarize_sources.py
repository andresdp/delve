#!/usr/bin/env python3
r"""Short LLM summaries of a case's sources, stored for the design-space wiki.

For each source with downloaded text (``benchmark/<case>/sources/text/sNN.md``,
from ``fetch_sources.py``), asks the LLM for a 2-3 sentence neutral summary and
writes ``benchmark/<case>/source_summaries.json``::

    {"model": ..., "generated": "YYYY-MM-DD", "prompt_version": "1",
     "summaries": {"s1": {"title": ..., "summary": ..., "words_read": 4321}, ...}}

The summaries are written in the model's own words (no quotes), so unlike the
source texts they can be committed. ``benchmark/export_wiki.py`` shows them on
the source pages, labeled as LLM-generated; the wiki export itself makes no LLM
call. Existing summaries are kept unless ``--force``; ``--only`` limits the run.

Usage::

    python benchmark/summarize_sources.py benchmark/c3-git-at-scale [--model openai/gpt-5.6-luna] [--force]
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from dotenv import load_dotenv  # noqa: E402

from taxonomy_generator.utils import load_chat_model  # noqa: E402

PROMPT_VERSION = "1"
MAX_WORDS = 12000
PROMPT = """Summarize the source below for a reader browsing a wiki of software-architecture design decisions.

Write 2-3 sentences, at most 60 words, in your own words (no quotations):
- what kind of document it is and which organization, system or project it concerns;
- which design problems or decisions it discusses.
Be neutral and factual; no marketing language, no evaluation of quality.

Title: {title}

Source text:
\"\"\"
{text}
\"\"\"

Summary:"""


def body(md: str) -> str:
    """Drop the provenance header written by fetch_sources.py."""
    return md.split("\n---\n", 1)[1] if "\n---\n" in md else md


async def summarize(model, title: str, text: str) -> tuple[str, int]:
    words = text.split()
    clipped = " ".join(words[:MAX_WORDS])
    reply = await model.ainvoke(PROMPT.format(title=title, text=clipped))
    content = reply.content if isinstance(reply.content, str) else " ".join(
        part.get("text", "") for part in reply.content if isinstance(part, dict))
    return " ".join(content.split()), min(len(words), MAX_WORDS)


async def run(case_dir: Path, model_name: str, force: bool, only: set[str] | None, concurrency: int) -> dict:
    out_path = case_dir / "source_summaries.json"
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    summaries = dict(existing.get("summaries") or {})
    rows = {r["id"]: r for r in csv.DictReader(open(case_dir / "sources.csv", encoding="utf-8"))}
    todo = []
    for sid, row in rows.items():
        text_file = case_dir / "sources" / "text" / f"{sid}.md"
        if (only and sid not in only) or not text_file.exists() or (sid in summaries and not force):
            continue
        todo.append((sid, row.get("title") or sid, body(text_file.read_text(encoding="utf-8"))))
    model = load_chat_model(model_name)
    sem = asyncio.Semaphore(concurrency)

    async def one(sid, title, text):
        async with sem:
            try:
                summary, n = await summarize(model, title, text)
                return sid, {"title": title, "summary": summary, "words_read": n}
            except Exception as exc:  # noqa: BLE001 - reported, the others still run
                print(f"  {sid}: failed ({str(exc)[:120]})", file=sys.stderr)
                return sid, None

    for sid, result in await asyncio.gather(*(one(*t) for t in todo)):
        if result:
            summaries[sid] = result
    out = {"model": model_name, "generated": dt.date.today().isoformat(), "prompt_version": PROMPT_VERSION,
           "summaries": dict(sorted(summaries.items(), key=lambda kv: int(kv[0][1:]) if kv[0][1:].isdigit() else 0))}
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{case_dir.name}: {len(todo)} summarized now, {len(out['summaries'])} stored -> {out_path}")
    return out


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("case_dir", type=Path, help="benchmark/<case> (with sources.csv and sources/text/)")
    ap.add_argument("--model", default="openai/gpt-5.6-luna", help="LLM (default: the study generation LLM)")
    ap.add_argument("--only", nargs="*", help="source ids to (re)summarize")
    ap.add_argument("--force", action="store_true", help="re-summarize sources that already have a summary")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args(argv)
    load_dotenv()
    asyncio.run(run(args.case_dir, args.model, args.force, set(args.only) if args.only else None, args.concurrency))
    return 0


if __name__ == "__main__":
    sys.exit(main())
