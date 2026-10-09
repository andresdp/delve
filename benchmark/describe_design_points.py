#!/usr/bin/env python3
r"""Short LLM descriptions of sampled design points, stored for the design-space wiki.

For each point in a ``*_design_points.json`` (``benchmark/design_points.py``),
asks the LLM to describe, in 2-3 sentences, the solution or solution fragment
that the combination of values implies, noting any evident tension between the
choices. The model sees each dimension (name and question) and the chosen value
(label, description, status), but not the point's group (attested / novel /
control) or system, so a description does not reflect how the point was sampled.

Writes ``<design points stem>_descriptions.json`` next to the input::

    {"model": ..., "generated": "YYYY-MM-DD", "prompt_version": "1",
     "descriptions": {"<signature>": {"point_id": "P012", "description": ...}, ...}}

The signature is the sorted ``dimension_id=value_id`` pairs, so the descriptions
also match the same points when ``benchmark/export_wiki.py --sample-design-points``
samples them again. The wiki export reads the file without any LLM call. Existing
descriptions are kept unless ``--force``.

Usage::

    python benchmark/describe_design_points.py examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350_design_points.json
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from dotenv import load_dotenv  # noqa: E402

from taxonomy_generator.evaluation.design_points import point_signature  # noqa: E402
from taxonomy_generator.utils import load_chat_model  # noqa: E402

PROMPT_VERSION = "1"
PROMPT = """A design space for "{domain}" was mined from engineering documents. Each dimension is one design
decision; each value is an alternative answer. Below is one combination of values, one per dimension.

{choices}

In 2-3 sentences (at most 70 words), describe the solution, or solution fragment, that this combination implies:
how the chosen values would work together in one system. If two choices are in evident tension or do not fit
together, say so briefly. Be concrete and neutral; do not invent details beyond the values given.

Description:"""


def choices_text(point: dict, dims: dict) -> str:
    lines = []
    for s in point.get("values") or []:
        d = dims.get(str(s.get("dimension_id"))) or {}
        question = d.get("description") or ""
        lines.append(f"- Dimension: {s.get('dimension')}" + (f" ({question})" if question else "")
                     + f"\n  Value: {s.get('label')}: {s.get('description')} [status: {s.get('status')}]")
    return "\n".join(lines)


async def run(dp_path: Path, model_name: str, force: bool, concurrency: int) -> dict:
    dp = json.loads(dp_path.read_text(encoding="utf-8"))
    run_file = Path(dp.get("run") or "")
    dims, domain = {}, ""
    if run_file.exists():
        tax = json.loads(run_file.read_text(encoding="utf-8"))
        dims = {str(c.get("id")): c for c in (tax.get("selected_clusters") or [])}
        domain = tax.get("taxonomy_name") or ""
    out_path = dp_path.with_name(dp_path.stem + "_descriptions.json")
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    descriptions = dict(existing.get("descriptions") or {})
    points = [p for s in dp.get("samples") or [] for g in (s.get("groups") or {}).values() for p in g]
    todo = [p for p in points if force or point_signature(p) not in descriptions]
    model = load_chat_model(model_name)
    sem = asyncio.Semaphore(concurrency)

    async def one(p):
        async with sem:
            try:
                reply = await model.ainvoke(PROMPT.format(domain=domain or "a software system",
                                                          choices=choices_text(p, dims)))
                content = reply.content if isinstance(reply.content, str) else " ".join(
                    part.get("text", "") for part in reply.content if isinstance(part, dict))
                return p, " ".join(content.split())
            except Exception as exc:  # noqa: BLE001 - reported, the others still run
                print(f"  {p.get('point_id')}: failed ({str(exc)[:120]})", file=sys.stderr)
                return p, None

    for p, text in await asyncio.gather(*(one(p) for p in todo)):
        if text:
            descriptions[point_signature(p)] = {"point_id": p.get("point_id"), "description": text}
    out = {"model": model_name, "generated": dt.date.today().isoformat(), "prompt_version": PROMPT_VERSION,
           "design_points": dp_path.name, "descriptions": dict(sorted(descriptions.items()))}
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(todo)} described now, {len(out['descriptions'])} stored -> {out_path}")
    return out


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("design_points", type=Path, help="*_design_points.json from benchmark/design_points.py")
    ap.add_argument("--model", default="openai/gpt-5.6-luna", help="LLM (default: the study generation LLM)")
    ap.add_argument("--force", action="store_true", help="re-describe points that already have a description")
    ap.add_argument("--concurrency", type=int, default=6)
    args = ap.parse_args(argv)
    load_dotenv()
    asyncio.run(run(args.design_points, args.model, args.force, args.concurrency))
    return 0


if __name__ == "__main__":
    sys.exit(main())
