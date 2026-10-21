#!/usr/bin/env python3
"""Second-judge reliability check for the two LLM-judged analyses (no human raters available).

Re-judges every item of the evidence check (``evidence_check.py``: ``pairs.json``) and of the unmatched-value check
(``unmatched_validity.py``: ``items.json``) with a second model, using the same prompts and output schemas, then
reports per question:

- agreement between the two judges (raw share and Cohen's kappa);
- each judge's per-method rates, to show whether the conclusions (L1 vs Delve citation support; Delve's valid extras)
  hold under the second judge.

This measures whether the verdicts are stable across judges, not whether they are right: it does not replace a
human check. The second judge must differ from the generator (``gpt-5.6-luna``) and from the first judge
(``gpt-5.4-mini``). Verdicts are cached per model under ``output/evaluation/report/judge_agreement/<model>/``.

Usage::

    python benchmark/judge_agreement.py --model openai/gpt-5.5
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
REPORT = ROOT / "output" / "evaluation" / "report"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_mod", ROOT / "benchmark" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def kappa(a: List[str], b: List[str]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


async def run_all(model_name: str, out: Path) -> Dict[str, Any]:
    from taxonomy_generator.utils import load_chat_model

    ev, um = _load("evidence_check"), _load("unmatched_validity")
    pairs = [p for p in json.loads((REPORT / "evidence_check" / "pairs.json").read_text(encoding="utf-8"))
             if p.get("label")]
    items = [it for it in json.loads((REPORT / "unmatched_validity" / "c1-ml-workflow" / "items.json").read_text(
        encoding="utf-8")) if it.get("assessment") and "error" not in it["assessment"]]
    corpora = {c: {d["id"]: d.get("content", "") for d in json.loads(
        (ROOT / "examples" / c / f"{c}_corpus.json").read_text(encoding="utf-8"))}
        for c in ("c1-ml-workflow", "c2-rl-monitoring")}
    from taxonomy_generator.settings import load_settings

    use_case = " ".join((load_settings(str(ROOT / "examples/c1-ml-workflow/c1_ml_workflow_config.yaml"))
                         .taxonomy.use_case or "").split())

    out.mkdir(parents=True, exist_ok=True)
    cache_path = out / "verdicts.jsonl"
    done: Dict[str, Dict] = {}
    if cache_path.exists():
        for line in cache_path.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            done[rec["key"]] = rec

    jobs = []
    for p in pairs:
        text = (corpora[p["case"]].get(p["passage_id"]) or "").strip()
        jobs.append(("B:" + ev.key(p), ev.Verdict,
                     ev.PROMPT.format(decision=p["decision"], option=p["option"], passage=text)))
    for it in items:
        passages = "\n\n".join(f"[{pid}] {' '.join((corpora['c1-ml-workflow'].get(pid) or '(missing)').split())}"
                               for pid in it["passages"])
        jobs.append(("A:" + um.key(it), um.Assessment,
                     um.PROMPT.format(use_case=use_case, decision=it["decision"], option=it["option"],
                                      expert="\n".join(f"- {t}" for t in it["expert"]), passages=passages or "(none)")))
    todo = [j for j in jobs if j[0] not in done]
    print(f"  {len(jobs)} items, {len(jobs) - len(todo)} cached, {len(todo)} to judge ({model_name})", flush=True)
    base = load_chat_model(model_name)
    models = {schema: base.with_structured_output(schema) for schema in (ev.Verdict, um.Assessment)}
    sem = asyncio.Semaphore(8)
    usage = Counter()

    async def one(job):
        k, schema, prompt = job
        async with sem:
            err = ""
            for attempt in range(3):
                try:
                    r = await models[schema].ainvoke(prompt)
                    usage["input_chars"] += len(prompt)
                    return {"key": k, **r.model_dump()}
                except Exception as exc:  # noqa: BLE001 - recorded, retried
                    err = f"{type(exc).__name__}: {exc}"[:300]
                    await asyncio.sleep(2 * (attempt + 1))
            return {"key": k, "error": err}

    with cache_path.open("a", encoding="utf-8") as fh:
        for fut in asyncio.as_completed([one(j) for j in todo]):
            rec = await fut
            if "error" not in rec:
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
            done[rec["key"]] = rec
    return {"pairs": pairs, "items": items, "done": done, "ev": ev, "um": um,
            "input_chars": usage["input_chars"], "judged": len(todo)}


def report(r: Dict[str, Any], model_name: str, out: Path) -> Path:
    ev, um, done = r["ev"], r["um"], r["done"]
    lines = [f"# Second-judge agreement: gpt-5.4-mini (judge 1) vs {model_name} (judge 2)", "",
             "Same items, prompts and schemas. Agreement shows stability across judges, not correctness.", "",
             "## Agreement", "", "| Check | Question | Items | Raw agreement | Cohen's κ |", "|---|---|---|---|---|"]

    b = [(p, done.get("B:" + ev.key(p))) for p in r["pairs"]]
    b = [(p, d) for p, d in b if d and "error" not in d]
    j1, j2 = [p["label"] for p, _ in b], [d["label"] for _, d in b]
    k = kappa(j1, j2)
    lines.append(f"| Citations | supported/partial/unsupported | {len(b)} | "
                 f"{sum(x == y for x, y in zip(j1, j2)) / len(b):.2f} | {'–' if k is None else f'{k:.2f}'} |")
    a = [(it, done.get("A:" + um.key(it))) for it in r["items"]]
    a = [(it, d) for it, d in a if d and "error" not in d]
    for q, f in (("in_scope", lambda x: str(x["in_scope"])), ("genuine_option", lambda x: str(x["genuine_option"])),
                 ("covered_by_expert", lambda x: x["covered_by_expert"]), ("evidence", lambda x: x["evidence"]),
                 ("valid extra (derived)", lambda x: str(um.valid_extra(x)))):
        x1, x2 = [f(it["assessment"]) for it, _ in a], [f(d) for _, d in a]
        k = kappa(x1, x2)
        lines.append(f"| Unmatched (C1) | {q} | {len(a)} | {sum(p == q_ for p, q_ in zip(x1, x2)) / len(a):.2f} | "
                     f"{'–' if k is None else f'{k:.2f}'} |")

    lines += ["", "## Do the conclusions hold?", "", "Citations: share supported (and values with ≥1 supported citation)",
              "", "| Case | Method | Judge 1 | Judge 2 |", "|---|---|---|---|"]
    for case in ("c1-ml-workflow", "c2-rl-monitoring"):
        for method in ("Delve", "L1"):
            g = [(p, d) for p, d in b if p["case"] == case and p["method"] == method]
            if not g:
                continue
            s1 = sum(p["label"] == "supported" for p, _ in g) / len(g)
            s2 = sum(d["label"] == "supported" for _, d in g) / len(g)
            vals: Dict[tuple, List] = {}
            for p, d in g:
                vals.setdefault((p["row"], p["value_id"]), []).append((p["label"], d["label"]))
            v1 = sum(any(x == "supported" for x, _ in v) for v in vals.values()) / len(vals)
            v2 = sum(any(y == "supported" for _, y in v) for v in vals.values()) / len(vals)
            lines.append(f"| {case} | {method} | {s1:.2f} ({v1:.2f}) | {s2:.2f} ({v2:.2f}) |")
    lines += ["", "Unmatched C1 values: share that are valid extras (and covered partly)", "",
              "| Method | Items | Judge 1 | Judge 2 |", "|---|---|---|---|"]
    for method in ("Delve", "L1"):
        g = [(it, d) for it, d in a if it["method"] == method]
        if not g:
            continue
        e1 = sum(um.valid_extra(it["assessment"]) for it, _ in g) / len(g)
        e2 = sum(um.valid_extra(d) for _, d in g) / len(g)
        p1 = sum(it["assessment"]["covered_by_expert"] == "partly" for it, _ in g) / len(g)
        p2 = sum(d["covered_by_expert"] == "partly" for _, d in g) / len(g)
        lines.append(f"| {method} | {len(g)} | {e1:.2f} ({p1:.2f}) | {e2:.2f} ({p2:.2f}) |")
    tokens = r["input_chars"] / 4
    lines += ["", f"Judge 2 calls this run: {r['judged']} (≈{tokens / 1e6:.2f}M input tokens, estimated from "
              "prompt length; output not counted)."]
    md = out / "judge_agreement.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--model", required=True)
    args = ap.parse_args(argv)
    if args.model.split("/")[-1] in ("gpt-5.6-luna", "gpt-5.4-mini"):
        print("the second judge must differ from the generator and from the first judge", file=sys.stderr)
        return 2
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    out = REPORT / "judge_agreement" / args.model.split("/")[-1]
    r = asyncio.run(run_all(args.model, out))
    md = report(r, args.model, out)
    print(md.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
