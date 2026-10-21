#!/usr/bin/env python3
"""Human spot-check of the LLM judges: a blind rating sheet, then agreement with the judges.

Two LLM-judged analyses rest on ``gpt-5.4-mini``: the unmatched-value check (``unmatched_validity.py``) and the
evidence check (``evidence_check.py``). This samples items from both, hides the method and the judge's verdict, and
writes a sheet for two raters; ``score`` then reports rater–rater and rater–judge agreement (raw agreement and
Cohen's kappa) per question.

- Part A (unmatched values, C1): ``--a`` items, half Delve and half L1 when possible. Questions as the judge's:
  in scope (y/n), genuine option (y/n), covered by an expert option (yes/partly/no), evidence
  (supported/partial/unsupported).
- Part B (citations, C1 and C2): ``--b`` (value, passage) pairs, half Delve and half L1: supported/partial/unsupported.

Files (``output/evaluation/report/spot_check/``, gitignored: the sheet quotes source passages, which must not be
committed): ``sheet_A.csv``, ``sheet_B.csv`` (open in a spreadsheet; fill the ``r1_*`` and ``r2_*`` columns),
``key.json`` (method and judge verdicts; do not open while rating), ``INSTRUCTIONS.md``.

Usage::

    python benchmark/spot_check.py make
    python benchmark/spot_check.py score
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "output" / "evaluation" / "report"
OUT = REPORT / "spot_check"
A_QUESTIONS = {"in_scope": ("y", "n"), "genuine": ("y", "n"), "covered": ("yes", "partly", "no"),
               "evidence": ("supported", "partial", "unsupported")}
B_QUESTIONS = {"evidence": ("supported", "partial", "unsupported")}

INSTRUCTIONS = """# Spot-check instructions

Two raters, working independently (do not discuss items until both are done). Do not open `key.json`.
Open each CSV in a spreadsheet (UTF-8), fill your columns (`r1_*` for rater 1, `r2_*` for rater 2) with exactly
one of the allowed values, and save as CSV under the same name.

## Sheet A: options outside the expert model (C1)

Use case (C1): {use_case}

Each row is one option of a mined design space that the automatic matcher did not match to the expert model.
You see its decision, the option, the 5 closest expert options, and up to 3 passages the option cites.

- `in_scope` (y/n): is the option relevant to the use case (not another problem or lifecycle stage)?
- `genuine` (y/n): is it a real alternative answer to its decision that a designer could choose, rather than a
  property, an outcome, a tool or product name, or a restatement of the decision?
- `covered` (yes/partly/no): does one of the listed expert options already express it (yes), overlap it
  substantially (partly), or neither (no)?
- `evidence` (supported/partial/unsupported): does at least one cited passage clearly describe the option
  (supported), touch it loosely (partial), or none (unsupported)?

## Sheet B: citations

Each row is one option with one passage it cites. Does the passage describe this option as an answer to this
decision (mentions, adopts, recommends, considers or rejects it, in any words)?

- `evidence`: supported / partial / unsupported (same meaning as above).

When done, run `python benchmark/spot_check.py score`.
"""


def make(n_a: int, n_b: int, seed: int) -> None:
    rng = random.Random(seed)
    corpora = {c: {d["id"]: " ".join((d.get("content") or "").split()) for d in json.loads(
        (ROOT / "examples" / c / f"{c}_corpus.json").read_text(encoding="utf-8"))}
        for c in ("c1-ml-workflow", "c2-rl-monitoring")}
    key: Dict[str, Dict] = {}

    items = [it for it in json.loads((REPORT / "unmatched_validity" / "c1-ml-workflow" / "items.json").read_text(
        encoding="utf-8")) if it.get("assessment") and "error" not in it["assessment"]]
    a_rows = []
    for method, k in (("Delve", n_a - n_a // 2), ("L1", n_a // 2)):
        pool = [it for it in items if it["method"] == method]
        for it in rng.sample(pool, min(k, len(pool))):
            a = it["assessment"]
            a_rows.append(({"decision": it["decision"], "option": it["option"],
                            "expert_options": "\n".join(f"- {t}" for t in it["expert"]),
                            "passages": "\n\n".join(f"[{p}] {corpora['c1-ml-workflow'].get(p, '(missing)')}"
                                                    for p in it["passages"])},
                           {"method": method, "row": it["row"], "value_id": it["value_id"],
                            "judge": {"in_scope": "y" if a["in_scope"] else "n",
                                      "genuine": "y" if a["genuine_option"] else "n",
                                      "covered": a["covered_by_expert"], "evidence": a["evidence"]}}))
    rng.shuffle(a_rows)

    pairs = [p for p in json.loads((REPORT / "evidence_check" / "pairs.json").read_text(encoding="utf-8"))
             if p.get("label")]
    b_rows = []
    for method, k in (("Delve", n_b - n_b // 2), ("L1", n_b // 2)):
        pool = [p for p in pairs if p["method"] == method]
        for p in rng.sample(pool, min(k, len(pool))):
            b_rows.append(({"case": p["case"], "decision": p["decision"], "option": p["option"],
                            "passage": f"[{p['passage_id']}] {corpora[p['case']].get(p['passage_id'], '(missing)')}"},
                           {"method": method, "row": p["row"], "value_id": p["value_id"],
                            "passage_id": p["passage_id"], "judge": {"evidence": p["label"]}}))
    rng.shuffle(b_rows)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows, questions in (("A", a_rows, A_QUESTIONS), ("B", b_rows, B_QUESTIONS)):
        rater_cols = [f"r{r}_{q}" for r in (1, 2) for q in questions]
        path = OUT / f"sheet_{name}.csv"
        with path.open("w", newline="", encoding="utf-8-sig") as fh:      # BOM: spreadsheets read it as UTF-8
            fields = ["id", *rows[0][0].keys(), *rater_cols]
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for i, (shown, hidden) in enumerate(rows, start=1):
                item_id = f"{name}{i:02d}"
                writer.writerow({"id": item_id, **shown, **{c: "" for c in rater_cols}})
                key[item_id] = hidden
    (OUT / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    from taxonomy_generator.settings import load_settings

    use_case = load_settings(str(ROOT / "examples/c1-ml-workflow/c1_ml_workflow_config.yaml")).taxonomy.use_case
    (OUT / "INSTRUCTIONS.md").write_text(INSTRUCTIONS.format(use_case=" ".join((use_case or "").split())),
                                         encoding="utf-8")
    print(f"-> {OUT}: sheet_A.csv ({len(a_rows)} items), sheet_B.csv ({len(b_rows)} items), INSTRUCTIONS.md")


def kappa(a: List[str], b: List[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def score() -> int:
    key = json.loads((OUT / "key.json").read_text(encoding="utf-8"))
    lines = ["# Spot-check agreement", "",
             "| Sheet | Question | Items | R1–R2 agree | R1–R2 κ | R1–judge agree | R1–judge κ | R2–judge agree | "
             "R2–judge κ |", "|" + "---|" * 9]
    for name, questions in (("A", A_QUESTIONS), ("B", B_QUESTIONS)):
        with (OUT / f"sheet_{name}.csv").open(encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        for q, allowed in questions.items():
            trip = [(r[f"r1_{q}"].strip().lower(), r[f"r2_{q}"].strip().lower(), key[r["id"]]["judge"][q])
                    for r in rows]
            bad = [r["id"] for r, t in zip(rows, trip) if (t[0] and t[0] not in allowed) or (t[1] and t[1] not in allowed)]
            if bad:
                print(f"sheet {name}, {q}: values outside {allowed} in {', '.join(bad)}", file=sys.stderr)
                return 1
            cells = []
            for i, j in ((0, 1), (0, 2), (1, 2)):
                pairs = [(t[i], t[j]) for t in trip if t[i] and t[j]]
                agree = sum(x == y for x, y in pairs) / len(pairs) if pairs else None
                k = kappa([x for x, _ in pairs], [y for _, y in pairs])
                cells += ["–" if agree is None else f"{agree:.2f}", "–" if k is None else f"{k:.2f}"]
            n = sum(1 for t in trip if t[0] or t[1])
            lines.append(f"| {name} | {q} | {n} | " + " | ".join(cells) + " |")
    md = OUT / "agreement.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md.read_text(encoding="utf-8"))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    mk = sub.add_parser("make")
    mk.add_argument("--a", type=int, default=30)
    mk.add_argument("--b", type=int, default=30)
    mk.add_argument("--seed", type=int, default=7)
    sub.add_parser("score")
    args = ap.parse_args(argv)
    sys.path.insert(0, str(ROOT / "src"))
    if args.command == "make":
        make(args.a, args.b, args.seed)
        return 0
    return score()


if __name__ == "__main__":
    sys.exit(main())
