#!/usr/bin/env python3
"""Build C2's ground-truth model view by statically parsing the replication package.

The C2 study (Fang, Warnett & Zdun) ships its design space as CodeableModels
code (``src/model/model.py``). This script reads that file with Python's
``ast`` module, without executing it or installing CodeableModels:

- ``x = CClass(<metaclass>, "Name")`` declares a decision, an option
  (``practice``/``pattern``) or a force; ``x = y`` is an alias;
- ``add_force_relations({option: {force: stereotype}})`` (inline or through a
  named dictionary) declares option-force impacts;
- ``add_decision_option_link(decision, option, [option_name], option_description=...)``
  links an option to a decision;
- ``add_links({a: b}, stereotype_instances=[...], label=...)`` links decisions.

Stereotypes appear in the model only as variable names; the metamodel
(``src/metamodels/guidance_metamodel.py``) is parsed the same way to map each
variable to its label and kind (force impact, next-decision link, dependency).
Descriptions come from the model (``description`` tagged value, or the
positional ``option_name`` text), with the ADD catalogue memo
(``memos/add-catalogue.md``) as fallback; the memo also gives each decision's
question and each force's per-decision driver text. A construct the parser
cannot read statically stops it (``UnsupportedConstruct``) instead of guessing.

The authors' generated PlantUML views (``_generated/rl_monitoring_adds/``) are an
independent cross-check: every difference in decisions, options, forces,
option links and impacts is listed.

Usage: ``python benchmark/parse_c2_model.py [--package DIR] [--out PATH]``
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gt_format  # noqa: E402

DEFAULT_PACKAGE = HERE / "c2-rl-monitoring" / "replication_package"
DEFAULT_OUT = HERE / "c2-rl-monitoring" / "gt" / "gt_model.json"
MODEL_REL = "src/model/model.py"
METAMODEL_REL = "src/metamodels/guidance_metamodel.py"
MEMO_REL = "memos/add-catalogue.md"
GENERATED_REL = "_generated/rl_monitoring_adds/all_view_with_forces.txt"
ZENODO_DOI = "10.5281/zenodo.20305497"

KIND_BY_METACLASS = {
    "decision": "decision",
    "practice": "option", "pattern": "option", "design_solution": "option",
    "do_nothing_design_solution": "option",
    "force": "force",
}
KIND_BY_PARENT = {
    "force_impact_type": "impact",
    "solutions_to_next_decisions_relation_type": "next_decision",
    "design_solution_dependency_type": "dependency",
    "decision_type": "decision_type",
}
MODEL_CALLS = ("CClass", "add_decision_option_link", "add_force_relations", "add_links")
HYPHENS = "‐‑‒–—−­"


class UnsupportedConstruct(ValueError):
    """The model uses a construct that cannot be read statically."""


# --------------------------------------------------------------------------- names

def normalize_name(name: str) -> str:
    """Normalize a name for matching: NFKC, hyphen variants to '-', whitespace, case."""
    text = unicodedata.normalize("NFKC", name)
    for ch in HYPHENS:
        text = text.replace(ch, "-")
    return re.sub(r"\s+", " ", text).strip().casefold()


def split_camel(name: str) -> str:
    """'DetectionLatency' -> 'Detection Latency'; names with spaces are kept."""
    if " " in name.strip():
        return name
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)


def slug(name: str) -> str:
    """Element id from a class name: words joined by '_', lower case."""
    text = normalize_name(split_camel(name))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


# ----------------------------------------------------------------------- metamodel

def _name(node: ast.AST) -> Optional[str]:
    return node.id if isinstance(node, ast.Name) else None


def _str(node: ast.AST) -> Optional[str]:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _call_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Call):
        return _name(node.func)
    return None


def parse_metamodel(source: str) -> Dict[str, Dict[str, str]]:
    """Map each stereotype variable of the metamodel to its label and kind."""
    stereotypes: Dict[str, Dict[str, str]] = {}
    for stmt in ast.parse(source).body:
        if not (isinstance(stmt, ast.Assign) and _call_name(stmt.value) == "CStereotype"):
            continue
        call = stmt.value
        label = _str(call.args[0]) if call.args else None
        parent = next((_name(kw.value) for kw in call.keywords if kw.arg == "superclasses"), None)
        kind = KIND_BY_PARENT.get(parent or "")
        if label is None or kind is None:
            continue
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                stereotypes[target.id] = {"label": label, "kind": kind}
    return stereotypes


# --------------------------------------------------------------------------- model

def _function_call_ids(tree: ast.Module) -> Set[int]:
    """ids of call nodes inside function definitions (helpers, not model content)."""
    inside: Set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    inside.add(id(sub))
    return inside


def parse_model(source: str, stereotypes: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """Read elements, option links, impacts and decision links from model source code."""
    tree = ast.parse(source)
    elements: Dict[str, Dict[str, Any]] = {}  # canonical variable -> element
    alias: Dict[str, str] = {}  # any variable -> canonical variable
    dicts: Dict[str, ast.Dict] = {}
    option_links: List[Dict[str, Any]] = []
    impacts: List[Dict[str, Any]] = []
    decision_links: List[Dict[str, Any]] = []
    handled: Set[int] = set()

    def resolve(node: ast.AST, what: str, line: int) -> str:
        var = _name(node)
        if var is None or var not in alias:
            raise UnsupportedConstruct(f"line {line}: {what} is not a known element ({ast.unparse(node)})")
        return alias[var]

    def stereotype(node: ast.AST, line: int) -> Dict[str, str]:
        var = _name(node)
        if var is None or var not in stereotypes:
            raise UnsupportedConstruct(f"line {line}: unknown stereotype ({ast.unparse(node)})")
        return stereotypes[var]

    def read_impacts(node: ast.AST, line: int) -> None:
        if isinstance(node, ast.Name) and node.id in dicts:
            node = dicts[node.id]
        if not isinstance(node, ast.Dict):
            raise UnsupportedConstruct(f"line {line}: add_force_relations needs a literal or named dict")
        for opt_node, forces_node in zip(node.keys, node.values):
            if not isinstance(forces_node, ast.Dict):
                raise UnsupportedConstruct(f"line {line}: force impacts must be a literal dict")
            opt = resolve(opt_node, "impact option", line)
            for force_node, st_node in zip(forces_node.keys, forces_node.values):
                st = stereotype(st_node, line)
                if st["kind"] != "impact":
                    raise UnsupportedConstruct(f"line {line}: {st['label']!r} is not a force impact stereotype")
                impacts.append({"option": opt, "force": resolve(force_node, "impact force", line),
                                "impact": st["label"], "line": force_node.lineno})

    for stmt in tree.body:
        line = getattr(stmt, "lineno", 0)
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            target = stmt.targets[0].id
            value = stmt.value
            if _call_name(value) == "CClass":
                handled.add(id(value))
                meta = _name(value.args[0]) if value.args else None
                name = _str(value.args[1]) if len(value.args) > 1 else None
                if meta not in KIND_BY_METACLASS or name is None:
                    raise UnsupportedConstruct(f"line {line}: CClass with unsupported arguments")
                elements[target] = {"var": target, "kind": KIND_BY_METACLASS[meta], "name": name, "line": line}
                alias[target] = target
            elif isinstance(value, ast.Name) and value.id in alias:
                alias[target] = alias[value.id]
            elif isinstance(value, ast.Dict):
                dicts[target] = value
            continue
        if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
            continue
        call = stmt.value
        func = _call_name(call)
        kwargs = {kw.arg: kw.value for kw in call.keywords}
        if func == "add_force_relations":
            handled.add(id(call))
            read_impacts(call.args[0], line)
        elif func == "add_decision_option_link":
            handled.add(id(call))
            dec = resolve(call.args[0], "linked decision", line)
            opt = resolve(call.args[1], "linked option", line)
            desc, desc_source = None, ""
            if "option_description" in kwargs:
                desc, desc_source = _str(kwargs["option_description"]), "model"
            elif len(call.args) > 2 or "option_name" in kwargs:
                desc = _str(call.args[2] if len(call.args) > 2 else kwargs["option_name"])
                desc_source = "model_positional"
            if desc_source and desc is None:
                raise UnsupportedConstruct(f"line {line}: option description is not a string literal")
            option_links.append({"decision": dec, "option": opt, "description": desc or "",
                                 "description_source": desc_source, "line": line})
        elif func == "add_links":
            handled.add(id(call))
            mapping = call.args[0] if call.args else None
            if not isinstance(mapping, ast.Dict) or len(mapping.keys) != 1:
                raise UnsupportedConstruct(f"line {line}: add_links needs a one-entry literal dict")
            st_node = kwargs.get("stereotype_instances")
            st_nodes = st_node.elts if isinstance(st_node, (ast.List, ast.Tuple)) else [st_node] if st_node else []
            labels = []
            for node in st_nodes:
                st = stereotype(node, line)
                if st["kind"] not in ("next_decision", "dependency"):
                    raise UnsupportedConstruct(f"line {line}: {st['label']!r} is not a link stereotype")
                labels.append(st["label"])
            label = _str(kwargs["label"]) if "label" in kwargs else ""
            decision_links.append({"from": resolve(mapping.keys[0], "link source", line),
                                   "to": resolve(mapping.values[0], "link target", line),
                                   "stereotypes": labels, "label": label or "", "line": line})

    # Every model call outside helper functions must have been read above.
    in_functions = _function_call_ids(tree)
    for node in ast.walk(tree):
        if (_call_name(node) in MODEL_CALLS and id(node) not in handled and id(node) not in in_functions):
            raise UnsupportedConstruct(
                f"line {node.lineno}: {_call_name(node)} call that cannot be read statically "
                f"({ast.unparse(node)[:80]})"
            )

    return {"elements": elements, "option_links": option_links, "impacts": impacts,
            "decision_links": decision_links}


# ---------------------------------------------------------------------------- memo

def _table_rows(lines: List[str]) -> List[Tuple[str, str]]:
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and not set(cells[0]) <= set("-: ") and cells[0] not in ("Option", "Driver"):
            rows.append((cells[0], cells[1]))
    return rows


def parse_memo(text: str) -> Dict[str, Dict[str, Any]]:
    """ADD catalogue memo -> {normalized decision name: question, trade-off, options, drivers}."""
    sections: Dict[str, Dict[str, Any]] = {}
    current: Optional[Dict[str, Any]] = None
    block: Optional[str] = None
    for raw in text.splitlines():
        line = raw.strip()
        heading = re.match(r"^##\s+ADD\s+(\d+):\s*(.+)$", line)
        if heading:
            current = {"number": int(heading.group(1)), "name": heading.group(2).strip(), "question": "",
                       "tradeoff": "", "options": {}, "drivers": []}
            sections[normalize_name(current["name"])] = current
            block = None
            continue
        if current is None:
            continue
        if line.startswith("### "):
            block = "options" if "Option" in line else "drivers" if "Driver" in line else None
            continue
        question = re.match(r"^\*\*Question\.\*\*\s*(.+)$", line)
        tradeoff = re.match(r"^\*\*Key trade.off\.\*\*\s*(.+)$", line)
        if question:
            current["question"] = question.group(1).strip()
        elif tradeoff:
            current["tradeoff"] = tradeoff.group(1).strip()
        elif line.startswith("|") and block:
            for name, desc in _table_rows([line]):
                if block == "options":
                    current["options"][normalize_name(name)] = desc
                else:
                    current["drivers"].append((name, desc))
    return sections


# ----------------------------------------------------------------------- the view

def build_view(model: Dict[str, Any], memo: Dict[str, Dict[str, Any]], provenance: Dict[str, Any],
               model_ref: str = MODEL_REL, memo_ref: str = MEMO_REL) -> Dict[str, Any]:
    """Assemble the ground-truth model view and record discrepancies in its provenance."""
    discrepancies: List[str] = []
    elements = model["elements"]
    ids: Dict[str, str] = {}
    for var, el in elements.items():
        ids[var] = var if el["kind"] == "decision" else slug(el["name"])
    seen: Dict[str, str] = {}
    for var, el_id in ids.items():
        if el_id in seen:
            raise UnsupportedConstruct(f"id collision '{el_id}' for {seen[el_id]} and {var}")
        seen[el_id] = var

    by_kind = {kind: [el for el in elements.values() if el["kind"] == kind]
               for kind in ("decision", "option", "force")}
    memo_by_decision = {var: memo.get(normalize_name(el["name"])) for var, el in elements.items()
                        if el["kind"] == "decision"}

    decisions = []
    for el in by_kind["decision"]:
        section = memo_by_decision[el["var"]]
        if section is None:
            discrepancies.append(f"decision '{el['name']}' has no section in the memo")
        tradeoff = (section or {}).get("tradeoff", "")
        decisions.append({
            "id": ids[el["var"]], "name": el["name"], "question": (section or {}).get("question", ""),
            "decision_type": "unspecified",
            "description": f"Key trade-off: {tradeoff}" if tradeoff else "",
            "description_source": "memo" if tradeoff else "",
            "source": f"{model_ref}:{el['line']}",
        })

    links_by_option: Dict[str, List[Dict[str, Any]]] = {}
    for link in model["option_links"]:
        links_by_option.setdefault(link["option"], []).append(link)

    options = []
    for el in by_kind["option"]:
        links = links_by_option.get(el["var"], [])
        dec_ids = list(dict.fromkeys(ids[lk["decision"]] for lk in links))
        desc, desc_source = "", ""
        for lk in links:
            if lk["description"]:
                if desc and lk["description"] != desc:
                    discrepancies.append(f"option '{el['name']}' has different descriptions on its links")
                desc, desc_source = desc or lk["description"], desc_source or lk["description_source"]
        if not desc:
            # Memo fallback: the sections of the option's decisions first, then any section.
            linked = [memo_by_decision.get(lk["decision"]) for lk in links]
            for section in [s for s in linked if s] + list(memo.values()):
                memo_desc = section["options"].get(normalize_name(el["name"]))
                if memo_desc:
                    desc, desc_source = memo_desc, "memo"
                    break
        option = {"id": ids[el["var"]], "name": el["name"], "decision_ids": dec_ids, "description": desc,
                  "description_source": desc_source,
                  "source": f"{model_ref}:{el['line']}" + "".join(f", {model_ref}:{lk['line']}" for lk in links)}
        if not dec_ids:
            option["unattached"] = True
            forces = sorted(elements[i["force"]]["name"] for i in model["impacts"] if i["option"] == el["var"])
            discrepancies.append(
                f"option '{el['name']}' is unattached (no decision link; forces: {', '.join(forces) or 'none'}); "
                "excluded from scoring"
            )
        options.append(option)

    forces = [{"id": ids[el["var"]], "name": el["name"], "description": "", "description_source": "",
               "source": f"{model_ref}:{el['line']}"} for el in by_kind["force"]]
    force_by_name = {normalize_name(el["name"]): el["var"] for el in by_kind["force"]}

    decision_forces = []
    for var, section in memo_by_decision.items():
        if not section:
            continue
        model_options = {normalize_name(elements[lk["option"]]["name"])
                         for lk in model["option_links"] if lk["decision"] == var}
        for memo_option in section["options"]:
            if memo_option not in model_options:
                discrepancies.append(f"memo option '{memo_option}' of ADD {section['number']} is not linked "
                                     "to that decision in the model")
        for opt in sorted(model_options - set(section["options"])):
            discrepancies.append(f"model option '{opt}' of ADD {section['number']} is not in the memo's options table")
        for driver, text in section["drivers"]:
            base = re.sub(r"\s*\(.*\)\s*$", "", driver)
            force_var = force_by_name.get(normalize_name(base))
            if force_var is None:
                discrepancies.append(f"memo driver '{driver}' of ADD {section['number']} matches no force")
                continue
            decision_forces.append({"decision_id": ids[var], "force_id": ids[force_var], "text": text,
                                    "source": f"{memo_ref}, ADD {section['number']}, Decision Drivers"
                                              + (f" ('{driver}')" if base != driver else "")})

    impacts = [{"option_id": ids[i["option"]], "force_id": ids[i["force"]], "impact": i["impact"],
                "source": f"{model_ref}:{i['line']}"} for i in model["impacts"]]
    decision_links = [{"from": ids[lk["from"]], "to": ids[lk["to"]], "stereotypes": lk["stereotypes"],
                       "label": lk["label"], "source": f"{model_ref}:{lk['line']}"}
                      for lk in model["decision_links"]]

    return {
        "format_version": gt_format.FORMAT_VERSION,
        "study": "c2-rl-monitoring",
        "view": "model",
        "provenance": {**provenance, "discrepancies": discrepancies},
        "decisions": decisions, "options": options, "forces": forces,
        "decision_forces": decision_forces, "impacts": impacts, "decision_links": decision_links,
    }


# ------------------------------------------------------------- generated views

def _plantuml_label(raw: str) -> Tuple[str, str]:
    text = raw.replace("<b>", "").replace("</b>", "").replace("\\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    name, _, kind = text.rpartition(" : ")
    return name.strip(), kind.strip()


def parse_plantuml(text: str) -> Dict[str, Set]:
    """Names, option links and impacts of a generated PlantUML view (formatting stripped)."""
    names: Dict[str, Tuple[str, str]] = {}
    out: Dict[str, Set] = {"decision_names": set(), "option_names": set(), "force_names": set(),
                           "option_links": set(), "impacts": set()}
    for line in text.splitlines():
        cls = re.match(r'^class "(.*)" as (\S+)$', line.strip())
        if cls:
            name, kind = _plantuml_label(cls.group(1))
            names[cls.group(2)] = (name, kind)
            key = {"Decision": "decision_names", "Practice": "option_names", "Pattern": "option_names",
                   "Force": "force_names"}.get(kind)
            if key:
                out[key].add(name)
            continue
        edge = re.match(r"^(\S+) --> (\S+): <<([^>]+)>>", line.strip())
        if edge and edge.group(1) in names and edge.group(2) in names:
            src, dst, st = names[edge.group(1)][0], names[edge.group(2)][0], edge.group(3)
            if st == "Option":
                out["option_links"].add((src, dst))
            elif st in gt_format.IMPACTS:
                out["impacts"].add((src, dst, st))
    return out


def cross_check(view: Dict[str, Any], generated: Dict[str, Set]) -> List[str]:
    """Differences between a parsed view and a generated PlantUML view."""
    names = {el["id"]: el["name"] for key in ("decisions", "options", "forces") for el in view[key]}
    ours = {
        "decision_names": {d["name"] for d in view["decisions"]},
        "option_names": {o["name"] for o in view["options"]},
        "force_names": {f["name"] for f in view["forces"]},
        "option_links": {(names[d], o["name"]) for o in view["options"] for d in o["decision_ids"]},
        "impacts": {(names[i["option_id"]], names[i["force_id"]], i["impact"]) for i in view["impacts"]},
    }
    diffs = []
    for key, label in (("decision_names", "decision"), ("option_names", "option"), ("force_names", "force"),
                       ("option_links", "option link"), ("impacts", "impact")):
        for item in sorted(ours[key] - generated[key], key=str):
            diffs.append(f"{label} {item} is parsed but not in the generated view")
        for item in sorted(generated[key] - ours[key], key=str):
            diffs.append(f"{label} {item} is in the generated view but not parsed")
    return diffs


# ---------------------------------------------------------------------------- main

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE, help="replication package folder")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output ground-truth file")
    args = parser.parse_args(argv)

    pkg = args.package
    files = {rel: pkg / rel for rel in (MODEL_REL, METAMODEL_REL, MEMO_REL, GENERATED_REL)}
    for rel, path in files.items():
        if not path.exists():
            print(f"missing {rel} in {pkg}", file=sys.stderr)
            return 2

    try:
        stereotypes = parse_metamodel(files[METAMODEL_REL].read_text(encoding="utf-8"))
        model = parse_model(files[MODEL_REL].read_text(encoding="utf-8"), stereotypes)
    except UnsupportedConstruct as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 3
    memo = parse_memo(files[MEMO_REL].read_text(encoding="utf-8"))
    provenance = {
        "package": f"C2 replication package (Zenodo {ZENODO_DOI}, Apache-2.0)",
        "parser": "benchmark/parse_c2_model.py (static ast parse; model not executed)",
        "files": {rel: {"sha256": _sha256(path)} for rel, path in files.items()},
    }
    view = build_view(model, memo, provenance)
    generated = parse_plantuml(files[GENERATED_REL].read_text(encoding="utf-8"))
    view["provenance"]["generated_view_differences"] = cross_check(view, generated)

    errors, warnings = gt_format.validate(view)
    if errors:
        for msg in errors:
            print(f"error: {msg}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(view, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    attached = [o for o in view["options"] if o["decision_ids"]]
    print(f"wrote {args.out}")
    print(f"  {len(view['decisions'])} decisions, {len(view['options'])} options "
          f"({len(attached)} attached), {len(view['forces'])} forces, {len(view['impacts'])} impacts, "
          f"{len(view['decision_forces'])} decision-force texts, {len(view['decision_links'])} decision links")
    print(f"  generated views: {len(generated['decision_names'])} decisions, {len(generated['option_names'])} "
          f"options, {len(generated['force_names'])} forces, {len(generated['option_links'])} option links, "
          f"{len(generated['impacts'])} impacts")
    for diff in view["provenance"]["generated_view_differences"]:
        print(f"  cross-check: {diff}")
    for msg in view["provenance"]["discrepancies"]:
        print(f"  discrepancy: {msg}")
    print(f"  {len(warnings)} validator warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
