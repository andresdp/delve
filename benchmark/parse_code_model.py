#!/usr/bin/env python3
"""Build a ground-truth model view by statically parsing a CodeableModels design-space model.

ADD studies built with CodeableModels (e.g. C1: Warnett & Zdun, ML workflow;
C2: Fang, Warnett & Zdun, RL monitoring) ship their design space as Python
code. This script reads that code with Python's ``ast`` module, without
executing it or installing CodeableModels:

- ``x = CClass(<metaclass>, "Name")`` declares a decision, an option
  (``practice``, ``pattern``, ``do_nothing_design_solution``) or a force;
  ``x = y`` is an alias; names may be literals joined with ``+``;
- ``add_force_relations({option: {force: stereotype}})`` (inline or through a
  named dictionary) declares option-force impacts;
- ``add_decision_option_link(decision, option, [option_name], option_description=...)``
  links an option to a decision;
- ``add_links({a: b}, stereotype_instances=..., label=...)`` and
  ``a.add_links(b, role_name="to"|"from", stereotype_instances=...)[0]`` link
  decisions and options: links between two decisions become decision links,
  links with an option at one end become solution links, and context links to
  domain classes are counted and skipped.

Stereotypes appear in a model only as variable names; the guidance metamodel
(``guidance_metamodel.py``) is parsed the same way to map each variable to its
label and kind (force impact, next-decision link, dependency, context).
Descriptions come from the model (``description`` tagged value, or the
positional ``option_name`` text), with an ADD catalogue memo, when the study
has one (C2: ``memos/add-catalogue.md``), as fallback; the memo also gives each
decision's question and each force's per-decision driver text. A construct the
parser cannot read statically stops it (``UnsupportedConstruct``) instead of
guessing.

The authors' generated PlantUML views are an independent cross-check: every
difference in the kinds those views show is listed. Study settings (package
paths, memo, generated views, output) are in ``STUDIES``.

Usage: ``python benchmark/parse_code_model.py --study c1|c2 [--package DIR] [--out PATH]``
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
from typing import Any

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
    "context_relations_type": "context",
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

def _name(node: ast.AST) -> str | None:
    return node.id if isinstance(node, ast.Name) else None


def _str(node: ast.AST) -> str | None:
    """Return a string literal, including literals joined with '+' ("a" + "b")."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _str(node.left), _str(node.right)
        return left + right if left is not None and right is not None else None
    return None


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        return _name(node.func)
    return None


def parse_metamodel(source: str) -> dict[str, dict[str, str]]:
    """Map each stereotype variable of the metamodel to its label and kind."""
    stereotypes: dict[str, dict[str, str]] = {}
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

def _function_call_ids(tree: ast.Module) -> set[int]:
    """Ids of call nodes inside function definitions (helpers, not model content)."""
    inside: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    inside.add(id(sub))
    return inside


def parse_model(source: str, stereotypes: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Read elements, option links, impacts and decision links from model source code."""
    tree = ast.parse(source)
    elements: dict[str, dict[str, Any]] = {}  # canonical variable -> element
    alias: dict[str, str] = {}  # any variable -> canonical variable
    dicts: dict[str, ast.Dict] = {}
    option_links: list[dict[str, Any]] = []
    impacts: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    context_links: list[int] = []
    handled: set[int] = set()

    def resolve(node: ast.AST, what: str, line: int) -> str:
        var = _name(node)
        if var is None or var not in alias:
            raise UnsupportedConstruct(f"line {line}: {what} is not a known element ({ast.unparse(node)})")
        return alias[var]

    def stereotype(node: ast.AST, line: int) -> dict[str, str]:
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

    def read_link(src: ast.AST, dst: ast.AST, st_node: ast.AST | None, label_node: ast.AST | None,
                  line: int) -> None:
        st_nodes = st_node.elts if isinstance(st_node, (ast.List, ast.Tuple)) else [st_node] if st_node else []
        kinds = [stereotype(node, line) for node in st_nodes]
        if kinds and all(st["kind"] == "context" for st in kinds):
            context_links.append(line)  # decision -> domain class; not design-space content
            return
        for st in kinds:
            if st["kind"] not in ("next_decision", "dependency"):
                raise UnsupportedConstruct(f"line {line}: {st['label']!r} is not a link stereotype")
        label = _str(label_node) if label_node is not None else ""
        links.append({"from": resolve(src, "link source", line), "to": resolve(dst, "link target", line),
                      "stereotypes": [st["label"] for st in kinds], "label": label or "", "line": line})

    def method_link(node: ast.AST) -> ast.Call | None:
        """``a.add_links(b, ...)`` or ``a.add_links(b, ...)[0]``."""
        if isinstance(node, ast.Subscript):
            node = node.value
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_links"):
            return node
        return None

    for stmt in tree.body:
        line = getattr(stmt, "lineno", 0)
        value = stmt.value if isinstance(stmt, (ast.Assign, ast.Expr)) else None
        call = method_link(value) if value is not None else None
        if call is not None:
            handled.add(id(call))
            kwargs = {kw.arg: kw.value for kw in call.keywords}
            role = _str(kwargs["role_name"]) if "role_name" in kwargs else "to"
            if len(call.args) != 1 or role not in ("to", "from"):
                raise UnsupportedConstruct(f"line {line}: add_links method call with unsupported arguments")
            src, dst = call.func.value, call.args[0]
            if role == "from":
                src, dst = dst, src
            read_link(src, dst, kwargs.get("stereotype_instances"), kwargs.get("label"), line)
            continue
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            target = stmt.targets[0].id
            if _call_name(value) == "CClass":
                handled.add(id(value))
                meta = _name(value.args[0]) if value.args else None
                name = _str(value.args[1]) if len(value.args) > 1 else None
                if meta not in KIND_BY_METACLASS or name is None:
                    raise UnsupportedConstruct(f"line {line}: CClass with unsupported arguments")
                name = re.sub(r"\s+", " ", name).strip()  # stray spaces, as the generated views show them
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
            target = mapping.values[0]
            # ``{a: b}`` or ``{a: [b, c]}``: one link per target
            for dst in target.elts if isinstance(target, (ast.List, ast.Tuple)) else [target]:
                read_link(mapping.keys[0], dst, kwargs.get("stereotype_instances"), kwargs.get("label"), line)

    # Every model call outside helper functions must have been read above.
    in_functions = _function_call_ids(tree)
    for node in ast.walk(tree):
        is_method_link = (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                          and node.func.attr == "add_links")
        if ((_call_name(node) in MODEL_CALLS or is_method_link)
                and id(node) not in handled and id(node) not in in_functions):
            raise UnsupportedConstruct(
                f"line {node.lineno}: {_call_name(node) or 'add_links'} call that cannot be read statically "
                f"({ast.unparse(node)[:80]})"
            )

    return {"elements": elements, "option_links": option_links, "impacts": impacts,
            "links": links, "context_links": len(context_links)}


# ---------------------------------------------------------------------------- memo

def _table_rows(lines: list[str]) -> list[tuple[str, str]]:
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and not set(cells[0]) <= set("-: ") and cells[0] not in ("Option", "Driver"):
            rows.append((cells[0], cells[1]))
    return rows


def parse_memo(text: str) -> dict[str, dict[str, Any]]:
    """ADD catalogue memo -> {normalized decision name: question, trade-off, options, drivers}."""
    sections: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    block: str | None = None
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

def build_view(model: dict[str, Any], memo: dict[str, dict[str, Any]], provenance: dict[str, Any],
               model_ref: str = MODEL_REL, memo_ref: str = MEMO_REL,
               study: str = "c2-rl-monitoring") -> dict[str, Any]:
    """Assemble the ground-truth model view and record discrepancies in its provenance."""
    discrepancies: list[str] = []
    elements = dict(model["elements"])  # copied: kinds may be corrected below
    # An element used as the decision of an option link is a decision, whatever
    # metaclass it was declared with (an authoring slip); report it.
    for var in dict.fromkeys(lk["decision"] for lk in model["option_links"]):
        el = elements[var]
        if el["kind"] != "decision":
            discrepancies.append(f"'{el['name']}' is declared as a {el['kind']} but has options; "
                                 "treated as a decision")
            elements[var] = {**el, "kind": "decision"}
    ids: dict[str, str] = {}
    for var, el in elements.items():
        ids[var] = var if el["kind"] == "decision" else slug(el["name"])
    # Two elements declared with the same name (an authoring slip) would share an
    # id: fall back to their variable names and report it.
    by_id: dict[str, list[str]] = {}
    for var, el_id in ids.items():
        by_id.setdefault(el_id, []).append(var)
    for el_id, variables in by_id.items():
        if len(variables) > 1:
            for var in variables:
                ids[var] = var
            discrepancies.append(
                f"elements {', '.join(variables)} share the name '{elements[variables[0]]['name']}'; "
                "their ids are their variable names"
            )
    if len(set(ids.values())) != len(ids):
        raise UnsupportedConstruct("element ids still collide after falling back to variable names")

    by_kind = {kind: [el for el in elements.values() if el["kind"] == kind]
               for kind in ("decision", "option", "force")}
    memo_by_decision = {var: memo.get(normalize_name(el["name"])) for var, el in elements.items()
                        if el["kind"] == "decision"}

    decisions = []
    for el in by_kind["decision"]:
        section = memo_by_decision[el["var"]]
        if section is None and memo:
            discrepancies.append(f"decision '{el['name']}' has no section in the memo")
        tradeoff = (section or {}).get("tradeoff", "")
        # Without a memo question, a decision named as a question (C1) is its own question.
        question = (section or {}).get("question", "") or (el["name"] if el["name"].rstrip().endswith("?") else "")
        decisions.append({
            "id": ids[el["var"]], "name": el["name"], "question": question,
            "decision_type": "unspecified",
            "description": f"Key trade-off: {tradeoff}" if tradeoff else "",
            "description_source": "memo" if tradeoff else "",
            "source": f"{model_ref}:{el['line']}",
        })

    links_by_option: dict[str, list[dict[str, Any]]] = {}
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
    # Links between two decisions are decision links; links with an option at
    # either end (an option that raises a next decision, option dependencies)
    # are solution links. Links to or from forces are not design-space links.
    decision_links, solution_links = [], []
    for lk in model["links"]:
        kinds = (elements[lk["from"]]["kind"], elements[lk["to"]]["kind"])
        record = {"from": ids[lk["from"]], "to": ids[lk["to"]], "stereotypes": lk["stereotypes"],
                  "label": lk["label"], "source": f"{model_ref}:{lk['line']}"}
        if kinds == ("decision", "decision"):
            decision_links.append(record)
        elif "force" in kinds:
            discrepancies.append(f"link with a force at line {lk['line']} ignored")
        else:
            solution_links.append(record)
    if model.get("context_links"):
        provenance = {**provenance, "context_links_skipped": model["context_links"]}

    view = {
        "format_version": gt_format.FORMAT_VERSION,
        "study": study,
        "view": "model",
        "provenance": {**provenance, "discrepancies": discrepancies},
        "decisions": decisions, "options": options, "forces": forces,
        "decision_forces": decision_forces, "impacts": impacts, "decision_links": decision_links,
    }
    if solution_links:
        view["solution_links"] = solution_links
    return view


# ------------------------------------------------------------- generated views

def _plantuml_label(raw: str) -> tuple[str, str]:
    text = raw.replace("<b>", "").replace("</b>", "").replace("\\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    name, _, kind = text.rpartition(" : ")
    return name.strip(), kind.strip()


def parse_plantuml(text: str) -> dict[str, set]:
    """Names, option links and impacts of a generated PlantUML view (formatting stripped)."""
    names: dict[str, tuple[str, str]] = {}
    out: dict[str, set] = {"decision_names": set(), "option_names": set(), "force_names": set(),
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


COMPARED = ("decision_names", "option_names", "force_names", "option_links", "impacts")


def cross_check(view: dict[str, Any], generated: dict[str, set], keys: tuple[str, ...] = COMPARED) -> list[str]:
    """Differences between a parsed view and generated PlantUML views, for the given kinds."""
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
        if key not in keys:
            continue
        for item in sorted(ours[key] - generated[key], key=str):
            diffs.append(f"{label} {item} is parsed but not in the generated view")
        for item in sorted(generated[key] - ours[key], key=str):
            diffs.append(f"{label} {item} is in the generated view but not parsed")
    return diffs


# ---------------------------------------------------------------------------- main

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


STUDIES: dict[str, dict[str, Any]] = {
    "c2": {
        "study": "c2-rl-monitoring",
        "package": DEFAULT_PACKAGE,
        "label": f"C2 replication package (Zenodo {ZENODO_DOI}, Apache-2.0)",
        "model": MODEL_REL, "metamodel": DEFAULT_PACKAGE / METAMODEL_REL, "memo": MEMO_REL,
        "generated": [GENERATED_REL],
        # all_view_with_forces shows every element, link and impact
        "compare": ("decision_names", "option_names", "force_names", "option_links", "impacts"),
        "out": DEFAULT_OUT,
    },
    "c1": {
        "study": "c1-ml-workflow",
        "package": HERE / "c1-ml-workflow" / "replication_package" / "ml_workflow_adds_v1",
        "label": "C1 replication package (Zenodo 10.5281/zenodo.5730291, Apache-2.0; downloaded, not committed)",
        "model": "add_models/ml_adds.py",
        # The C1 package does not ship the CodeableModels guidance metamodel; every
        # stereotype it imports is defined in the copy shipped with C2.
        "metamodel": DEFAULT_PACKAGE / METAMODEL_REL, "memo": None,
        "generated": "_generated/ml_adds/*.txt",
        # per-decision views without forces: compare decisions and option links
        "compare": ("decision_names", "option_links"),
        "out": HERE / "c1-ml-workflow" / "gt" / "gt_model.json",
    },
}


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--study", choices=sorted(STUDIES), default="c2")
    parser.add_argument("--package", type=Path, help="replication package folder (default: per study)")
    parser.add_argument("--out", type=Path, help="output ground-truth file (default: per study)")
    args = parser.parse_args(argv)
    cfg = STUDIES[args.study]
    pkg = args.package or cfg["package"]
    out = args.out or cfg["out"]

    model_path, metamodel_path = pkg / cfg["model"], cfg["metamodel"]
    memo_path = pkg / cfg["memo"] if cfg["memo"] else None
    generated_paths = ([pkg / g for g in cfg["generated"]] if isinstance(cfg["generated"], list)
                       else sorted(pkg.glob(cfg["generated"])))
    for path in [model_path, metamodel_path] + ([memo_path] if memo_path else []):
        if not path.exists():
            print(f"missing {path}", file=sys.stderr)
            return 2
    if not generated_paths:
        print(f"no generated views in {pkg}", file=sys.stderr)
        return 2

    try:
        stereotypes = parse_metamodel(metamodel_path.read_text(encoding="utf-8"))
        model = parse_model(model_path.read_text(encoding="utf-8"), stereotypes)
    except UnsupportedConstruct as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 3
    memo = parse_memo(memo_path.read_text(encoding="utf-8")) if memo_path else {}
    hashed = [model_path, metamodel_path] + ([memo_path] if memo_path else [])
    provenance = {
        "package": cfg["label"],
        "parser": "benchmark/parse_code_model.py (static ast parse; model not executed)",
        "files": {str(path.relative_to(HERE)): {"sha256": _sha256(path)} for path in hashed},
    }
    view = build_view(model, memo, provenance, model_ref=cfg["model"], study=cfg["study"])
    generated: dict[str, set] = {}
    for path in generated_paths:
        for key, items in parse_plantuml(path.read_text(encoding="utf-8")).items():
            generated.setdefault(key, set()).update(items)
    view["provenance"]["generated_view_differences"] = cross_check(view, generated, cfg["compare"])

    errors, warnings = gt_format.validate(view)
    if errors:
        for msg in errors:
            print(f"error: {msg}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(view, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    attached = [o for o in view["options"] if o["decision_ids"]]
    print(f"wrote {out}")
    print(f"  {len(view['decisions'])} decisions, {len(view['options'])} options "
          f"({len(attached)} attached), {len(view['forces'])} forces, {len(view['impacts'])} impacts, "
          f"{len(view['decision_forces'])} decision-force texts, {len(view['decision_links'])} decision links, "
          f"{len(view.get('solution_links', []))} solution links, "
          f"{model.get('context_links', 0)} context links skipped")
    print(f"  generated views ({len(generated_paths)} files): {len(generated['decision_names'])} decisions, "
          f"{len(generated['option_names'])} options, {len(generated['force_names'])} forces, "
          f"{len(generated['option_links'])} option links, {len(generated['impacts'])} impacts; "
          f"compared: {', '.join(cfg['compare'])}")
    for diff in view["provenance"]["generated_view_differences"]:
        print(f"  cross-check: {diff}")
    for msg in view["provenance"]["discrepancies"]:
        print(f"  discrepancy: {msg}")
    print(f"  {len(warnings)} validator warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
