#!/usr/bin/env python3
"""The blind human rating (validation layer 3): build the rating kit, then compute agreement and unblind.

``packets`` takes one repetition (default 1) of every brief and condition, renders each design as one packet
(the brief, then its ADRs) without the identifiers that reveal the condition (value ids, citations, the design
space headings, and any id of the M or E graph found in the text), and writes them under random codes:

- ``results/rating/packets/<code>.md``: the packets, to hand to the raters;
- ``results/rating/sheet-<rater>.csv``: one sheet per rater, packets in a different random order for each;
- ``results/rating/RUBRIC.md``: the rubric;
- ``results/rating-key/key.json``: code to session. Keep it from the raters until both sheets are complete.

It prints the packets whose text still mentions the design space (words such as "ddspace" or "design space"),
for a look before the kit goes out.

``agreement`` reads the two filled sheets: quadratic-weighted Cohen's kappa per item, and the packets where the
raters differ by two or more points (to discuss and resolve). With ``--unblind`` (after rating), it adds the
per-condition means of each item, from ``sheet-resolved.csv`` when present (a copy of one sheet with the
resolved scores), else from the mean of the two raters. Results go to ``results/rating/agreement.json``.

Usage::

    python study/cain2027/rating.py packets [--workspaces <folder>] [--rep 1] [--raters A,B] [--seed N]
    python study/cain2027/rating.py agreement [--raters A,B] [--unblind]
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import secrets
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
ITEMS = ("coverage", "tradeoffs", "fit", "correctness")
SCALE = (1, 2, 3, 4)
RUBRIC = """# Rating rubric

Rate each packet on its own: the brief, then one Architecture Decision Record (ADR) per design decision.
Score each item from 1 to 4 (1 = poor, 2 = weak, 3 = adequate, 4 = good) in your sheet, without consulting the
other rater. Use `notes` for anything that explains a low score.

1. **coverage**: the ADRs address the decisions this system needs.
2. **tradeoffs**: the options and their pros and cons are sound and relevant.
3. **fit**: the choices and rationale follow from the brief's requirements.
4. **correctness**: nothing is wrong or misleading.
"""
# Words that may reveal a design-space condition; reported, not removed (removing them could change meaning).
TELLS = re.compile(r"ddspace|design space|expert model|wiki|value id|passage", re.I)


def blind(doc: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the design without value ids and citations."""
    return {"decisions": [{**d, "chosen": {**d["chosen"], "value_id": None},
                           "alternatives": [{**a, "value_id": None, "citations": []} for a in d["alternatives"]]}
                          for d in doc["decisions"]],
            "uncovered": list(doc.get("uncovered") or [])}


def scrub(text: str, ids: Iterable[str]) -> str:
    """Replace graph ids that appear in free text (whole tokens, with or without backticks) by ``[ref]``.

    Only structured ids (``d:1``, ``v:9.6``, ``s04_p02``) are replaced, never a plain word.
    """
    for i in sorted({i for i in ids if i and re.search(r"[:_\d]", i)}, key=len, reverse=True):
        text = re.sub(rf"`?(?<![\w-]){re.escape(i)}(?![\w-])`?", "[ref]", text)
    return text


def packet(doc: Mapping[str, Any], brief: Mapping[str, Any], code: str, ids: Iterable[str] = ()) -> str:
    """Return one packet: the brief, then the blinded ADRs, then the open decisions."""
    files = design.render_adrs(blind(doc), brief["system"])
    parts = [f"# Packet {code}", "", "## Brief", "", f"**{brief['system']}**", "", brief["text"].strip(), ""]
    for n, text in enumerate(files.values(), 1):
        body = text.replace("\n* System: " + brief["system"] + "\n", "\n")
        parts += ["---", "", f"## ADR {n}", "", re.sub(r"^#", "###", body, flags=re.M).rstrip(), ""]
    if doc.get("uncovered"):
        parts += ["---", "", "## Decisions left open", ""] + [f"* {u}" for u in doc["uncovered"]] + [""]
    return scrub("\n".join(parts), ids).rstrip() + "\n"


def graph_ids(workspaces: Optional[Path]) -> Set[str]:
    """Node and passage ids of the M and E graphs (empty without workspaces)."""
    ids: Set[str] = set()
    for cond in design.SPACE_CONDITIONS if workspaces else ():
        graph = json.loads((workspaces / cond / "raw" / "graph.json").read_text(encoding="utf-8"))
        for n in graph.get("nodes") or []:
            ids.add(n["id"])
            ids |= {p.get("id") for p in n.get("passages") or [] if p.get("id")}
            ids |= {p.get("doc") for p in n.get("passages") or [] if p.get("doc")}
    return ids


def build_kit(rep: int, raters: Sequence[str], seed: Optional[int], workspaces: Optional[Path],
              results: Path = RESULTS, briefs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Write the packets, sheets, rubric and key; return the key."""
    kit, key_path = results / "rating", results / "rating-key" / "key.json"
    if key_path.exists() or kit.exists():
        raise SystemExit(f"a rating kit already exists ({kit}); remove it and its key to build a new one")
    briefs = {b["id"]: b for b in (briefs if briefs is not None else design.load_briefs())}
    sessions = [f"{b}-{c}-r{rep}" for b in briefs for c in ("N",) + design.SPACE_CONDITIONS]
    missing = [s for s in sessions if not (results / "designs" / f"{s}.json").is_file()]
    if missing:
        raise SystemExit(f"no design for {', '.join(missing)}")
    rng = random.Random(seed if seed is not None else secrets.randbits(64))
    codes = rng.sample(range(100, 1000), len(sessions))
    key = {f"P{code}": s for code, s in zip(codes, sessions)}
    ids = graph_ids(workspaces)
    (kit / "packets").mkdir(parents=True)
    tells = []
    for code, sid in key.items():
        doc = json.loads((results / "designs" / f"{sid}.json").read_text(encoding="utf-8"))
        text = packet(doc, briefs[sid.rsplit("-", 2)[0]], code, ids)
        (kit / "packets" / f"{code}.md").write_text(text, encoding="utf-8")
        if TELLS.search(text):
            tells.append(code)
    (kit / "RUBRIC.md").write_text(RUBRIC, encoding="utf-8")
    for rater in raters:
        order = list(key)
        rng.shuffle(order)
        with (kit / f"sheet-{rater}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["packet", *ITEMS, "notes"])
            w.writerows([[c, "", "", "", "", ""] for c in order])
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(json.dumps({"rep": rep, "seed": seed, "graph_ids_scrubbed": bool(ids), "packets": key},
                                   indent=2) + "\n", encoding="utf-8")
    for code in tells:
        print(f"{code}: mentions the design space; check the wording before rating")  # noqa: T201
    return key


def qwk(a: Sequence[int], b: Sequence[int], scale: Sequence[int] = SCALE) -> Optional[float]:
    """Quadratic-weighted Cohen's kappa of two raters on an ordinal scale (None when undefined)."""
    k, n = len(scale), len(a)
    if n == 0 or n != len(b):
        return None
    index = {v: i for i, v in enumerate(scale)}
    observed = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        observed[index[x]][index[y]] += 1
    rows = [sum(r) for r in observed]
    cols = [sum(observed[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * observed[i][j]
            den += w * rows[i] * cols[j] / n
    return None if den == 0 else 1 - num / den


def read_sheet(path: Path) -> Dict[str, Dict[str, int]]:
    """Return a filled sheet as packet -> item -> score; refuse missing or out-of-scale scores."""
    out = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            scores = {}
            for item in ITEMS:
                value = (row.get(item) or "").strip()
                if not value.isdigit() or int(value) not in SCALE:
                    raise SystemExit(f"{path.name}: packet {row['packet']} has no valid {item} score ({value!r})")
                scores[item] = int(value)
            out[row["packet"]] = scores
    return out


def agreement(a: Mapping[str, Mapping[str, int]], b: Mapping[str, Mapping[str, int]]) -> Dict[str, Any]:
    """Kappa per item, and the (packet, item) pairs where the raters differ by two or more points."""
    if set(a) != set(b):
        raise SystemExit("the two sheets rate different packets")
    codes = sorted(a)
    return {"kappa": {i: qwk([a[c][i] for c in codes], [b[c][i] for c in codes]) for i in ITEMS},
            "exact_agreement": {i: mean(a[c][i] == b[c][i] for c in codes) for i in ITEMS},
            "to_resolve": [{"packet": c, "item": i, "scores": [a[c][i], b[c][i]]}
                           for c in codes for i in ITEMS if abs(a[c][i] - b[c][i]) >= 2]}


def by_condition(scores: Mapping[str, Mapping[str, float]], key: Mapping[str, str]) -> Dict[str, Dict[str, float]]:
    """Per condition, the mean of each item over its packets."""
    out: Dict[str, Dict[str, float]] = {}
    for cond in sorted({s.rsplit("-", 2)[1] for s in key.values()}):
        codes = [c for c, s in key.items() if s.rsplit("-", 2)[1] == cond and c in scores]
        out[cond] = {i: mean(scores[c][i] for c in codes) for i in ITEMS} if codes else {}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("packets", help="build the blind rating kit")
    p.add_argument("--workspaces", type=Path, help="folder with M and E, to scrub their ids from the text")
    p.add_argument("--rep", type=int, default=1)
    p.add_argument("--raters", default="A,B")
    p.add_argument("--seed", type=int, help="for a reproducible kit (default: random, recorded in the key)")
    g = sub.add_parser("agreement", help="kappa per item; per-condition means with --unblind")
    g.add_argument("--raters", default="A,B")
    g.add_argument("--unblind", action="store_true", help="read the key (only after both sheets are complete)")
    args = parser.parse_args()
    results = RESULTS
    kit, key_path = results / "rating", results / "rating-key" / "key.json"
    raters = [r.strip() for r in args.raters.split(",") if r.strip()]
    if args.command == "packets":
        key = build_kit(args.rep, raters, args.seed, args.workspaces, results=results)
        print(f"{len(key)} packets in {kit}; key in {key_path.parent} (keep it from the raters)")  # noqa: T201
        return
    if len(raters) != 2:
        raise SystemExit("agreement needs exactly two raters")
    a, b = (read_sheet(kit / f"sheet-{r}.csv") for r in raters)
    out: Dict[str, Any] = {"raters": raters, **agreement(a, b)}
    if args.unblind:
        key = json.loads(key_path.read_text(encoding="utf-8"))["packets"]
        resolved = kit / "sheet-resolved.csv"
        out["raw_by_condition"] = by_condition({c: {i: (a[c][i] + b[c][i]) / 2 for i in ITEMS} for c in a}, key)
        if resolved.is_file():
            out["resolved_by_condition"] = by_condition(read_sheet(resolved), key)
        out["sessions"] = key
    (kit / "agreement.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))  # noqa: T201


if __name__ == "__main__":
    main()
