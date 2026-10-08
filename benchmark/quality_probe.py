#!/usr/bin/env python3
r"""Taxonomy quality probe (paper plan A11 and the "axis vs. value" problem).

For one saved run: audits every selected dimension (one design question? is each
value an option, a fact, an effect, a goal, or an option for another question?) and
checks a seeded, status-stratified sample of value → passage evidence links against
the passage text. The judge is an LLM (default ``openai/gpt-5.4-mini``, a different
model from the generator); its labels estimate rates and must be spot-checked.

Writes, into ``--out-dir`` (default ``<run folder>/probe/``):

- ``<run>_probe.json``: summaries plus every audit and link verdict;
- ``<run>_probe_links.csv``: the sampled links with verdict and reason, plus an empty
  ``human`` column for the spot-check. Passage text is not copied;
- ``<run>_probe_values.csv``: every audited value with its dimension's question, the
  judge's kind and reason, plus an empty ``human`` column.

``--resummarize`` recomputes the summary and sheets from an existing probe file
(no LLM calls).

Usage::

    python benchmark/quality_probe.py <run>_taxonomy_<ts>.json --corpus <case>_corpus.json [--links 40] [--seed 7]
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from dotenv import load_dotenv  # noqa: E402

from taxonomy_generator.evaluation.quality_probe import (  # noqa: E402
    audit_dimensions, check_links, sample_links, summarize_audits, summarize_links)
from taxonomy_generator.utils import load_chat_model  # noqa: E402


async def run(args) -> dict:
    path = Path(args.taxonomy)
    clusters = json.loads(path.read_text(encoding="utf-8")).get("selected_clusters") or []
    passages = {str(p["id"]): p["content"] for p in json.loads(Path(args.corpus).read_text(encoding="utf-8"))
                if isinstance(p, dict) and "id" in p}
    model = load_chat_model(args.judge)
    links = sample_links(clusters, args.links, args.seed)
    audits, verdicts = await asyncio.gather(audit_dimensions(model, clusters), check_links(model, links, passages))
    return {"run": str(path), "judge": args.judge, "seed": args.seed,
            "summary": {"dimensions": summarize_audits(audits), "links": summarize_links(verdicts)},
            "audits": [{k: v for k, v in a.items() if k != "values"} for a in audits], "links": verdicts}


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("taxonomy", help="saved run (*_taxonomy_<timestamp>.json)")
    parser.add_argument("--corpus", required=True, help="the run's corpus JSON (passage id → text)")
    parser.add_argument("--judge", default="openai/gpt-5.4-mini")
    parser.add_argument("--links", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--resummarize", action="store_true", help="reuse the existing probe file; no LLM calls")
    args = parser.parse_args(argv)
    load_dotenv()

    path = Path(args.taxonomy)
    out_dir = args.out_dir or path.parent / "probe"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = path.with_suffix("").name
    clusters = json.loads(path.read_text(encoding="utf-8")).get("selected_clusters") or []
    values_of = {str(c.get("id")): c.get("values") or [] for c in clusters}
    if args.resummarize:
        out = json.loads((out_dir / f"{stem}_probe.json").read_text(encoding="utf-8"))
        audits = [{**a, "values": values_of.get(a["id"], [])} for a in out["audits"]]
        out["summary"] = {"dimensions": summarize_audits(audits), "links": summarize_links(out["links"])}
    else:
        out = asyncio.run(run(args))
    (out_dir / f"{stem}_probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(out_dir / f"{stem}_probe_links.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["passage_id", "dimension", "value", "status", "verdict", "reason", "human"])
        for x in out["links"]:
            w.writerow([x["passage_id"], x["dimension"], f"{x['label']}: {x['description']}", x["status"],
                        x.get("verdict") or "ERROR", x.get("reason") or x.get("error", ""), ""])
    status_of = {str(v.get("id")): v for vals in values_of.values() for v in vals}
    with open(out_dir / f"{stem}_probe_values.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "question", "value_id", "value", "status", "kind", "reason", "human"])
        for a in out["audits"]:
            if not a.get("audit"):
                continue
            for vk in a["audit"]["values"]:
                v = status_of.get(vk["value_id"], {})
                w.writerow([a["name"], a["audit"]["decision_question"], vk["value_id"],
                            f"{v.get('label', '')}: {v.get('description', '')}", v.get("status", ""),
                            vk["kind"], vk["reason"], ""])
    s = out["summary"]
    print(json.dumps(s["dimensions"]["candidate_kind_rates"]), "focused:", s["dimensions"]["focused_rate"])
    print("links:", json.dumps(s["links"]["overall"]), "failed:", s["links"]["failed"])
    print(f"-> {out_dir / (stem + '_probe.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
