"""The design an agent returns, shared by the session runner and the scorer: schema, validation, briefs.

The schema is the one passed to ``codex exec --output-schema`` (strict structured output: every property
required, no extra properties). ``validate`` checks the subset of JSON Schema the file uses, so the study
needs no ``jsonschema`` dependency.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "design.schema.json"
PROMPT = HERE / "prompt.md"
BRIEFS = HERE / "briefs.yaml"
INPUTS = HERE / "inputs"
SPACE_CONDITIONS = ("M", "E")              # the conditions with a design space (N has none)
MANIFEST_COPY = "study-manifest.json"      # the input manifest, as copied into each workspace
_TYPES = {"object": dict, "array": list, "string": str, "null": type(None), "number": (int, float), "integer": int,
          "boolean": bool}
_KEY = re.compile(r"sk-[A-Za-z0-9_\-]{12,}")
_QUESTION = re.compile(r"^(how|what|where|when|which|who|why|should|whether|do|does|is|are|can)\b", re.I)


_RESULTS_NAME = re.compile(r"^results(-[A-Za-z0-9._-]+)?$")


def results_folder(name: str) -> Path:
    """The study's results folder ``name`` (``results`` or ``results-<label>``, e.g. one per agent model).

    The name pattern keeps every results folder under the raw-log ignore rule (``results*/raw/``).
    """
    if not _RESULTS_NAME.match(name):
        raise ValueError(f"results folder {name!r}: use 'results' or 'results-<label>' (letters, digits, . _ -)")
    return HERE / name


_FENCE = re.compile(r"^\s*```[A-Za-z]*\s*\n(.*)\n\s*```\s*$", re.S)


def unfence(text: str) -> str:
    """The reply without a Markdown code block around it (some models wrap their JSON in one)."""
    match = _FENCE.match(text)
    return match.group(1) if match else text


def prompt_text(prompt: Path, schema_in_prompt: bool = False) -> str:
    """The prompt sent to the agent; with ``schema_in_prompt``, the output schema is appended to it.

    Codex passes ``--output-schema`` to OpenAI models as structured output; models reached through a local
    provider (``--oss``) do not receive it, so they get the same schema as text instead.
    """
    text = prompt.read_text(encoding="utf-8")
    if not schema_in_prompt:
        return text
    return (text.rstrip("\n") + "\n\nThe required JSON format, as a JSON Schema (every property is required):"
            "\n\n```json\n" + SCHEMA.read_text(encoding="utf-8").strip()
            + "\n```\n\nReturn only the JSON object, not wrapped in a code block.\n")


def schema() -> Dict[str, Any]:
    """Return the design schema."""
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def matching_model() -> str:
    """Return the matcher's judge model, as pinned in the tracked run config (``models.matching_llm``)."""
    config = yaml.safe_load((INPUTS / "config.yaml").read_text(encoding="utf-8")) or {}
    return str((config.get("models") or {}).get("matching_llm") or "")


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(instance: Any, spec: Optional[Dict[str, Any]] = None, path: str = "$") -> List[str]:
    """Return the problems of ``instance`` against the schema (empty when it conforms)."""
    spec = schema() if spec is None else spec
    types = spec.get("type")
    if types is not None:
        allowed = tuple(_TYPES[t] for t in ([types] if isinstance(types, str) else types))
        if not isinstance(instance, allowed) or (isinstance(instance, bool) and bool not in allowed):
            return [f"{path}: expected {types}, got {type(instance).__name__}"]
    problems: List[str] = []
    if isinstance(instance, dict):
        props = spec.get("properties", {})
        problems += [f"{path}: missing {k}" for k in spec.get("required", []) if k not in instance]
        if spec.get("additionalProperties") is False:
            problems += [f"{path}: unexpected {k}" for k in instance if k not in props]
        for key, sub in props.items():
            if key in instance:
                problems += validate(instance[key], sub, f"{path}.{key}")
    elif isinstance(instance, list) and "items" in spec:
        for i, item in enumerate(instance):
            problems += validate(item, spec["items"], f"{path}[{i}]")
    return problems


def load_briefs(path: Path = BRIEFS) -> List[Dict[str, Any]]:
    """Return the briefs (id, system, text, forces)."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))["briefs"]


def redact(text: str, home: str, secrets: Iterable[str] = ()) -> str:
    """Remove API keys, the home folder and the user name from ``text``."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[key]")
    text = _KEY.sub("[key]", text)
    if home:
        text = text.replace(home.rstrip("/"), "~")
        user = Path(home).name
        if len(user) > 2:
            text = re.sub(rf"\b{re.escape(user)}\b", "[user]", text)
    return text


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "decision"


def _ids(value_id: Optional[str], citations: Iterable[str] = ()) -> str:
    """Return the identifiers of an option as inline code (empty when there are none)."""
    ids = ([value_id] if value_id else []) + list(citations)
    return " (" + ", ".join(f"`{i}`" for i in ids) + ")" if ids else ""


def adr_title(dec: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """Return an ADR's title and, when the agent worded the decision as a question, that question.

    MADR titles name the problem and the solution. A decision worded as a question ("How should predictions be
    served?") gets the chosen option as its title, with the question shown below it.
    """
    text = dec["decision"].strip()
    if text.endswith("?") or _QUESTION.match(text):
        return dec["chosen"]["label"], text
    return text, None


def render_adrs(doc: Dict[str, Any], system: str) -> Dict[str, str]:
    """Render a design as MADR-style Markdown ADRs, one file per decision (``0001-<slug>.md``)."""
    files = {}
    for n, dec in enumerate(doc["decisions"], 1):
        chosen = dec["chosen"]
        title, question = adr_title(dec)
        lines = [f"# {title}", ""] + ([f"*{question}*", ""] if question else [])
        lines += [f"* System: {system}", "", "## Context and Problem Statement", "",
                  dec["context"], "", "## Decision Drivers", ""]
        lines += [f"* {d}" for d in dec["drivers"]] or ["* (none stated)"]
        lines += ["", "## Considered Options", ""]
        lines += [f"* {a['label']}{_ids(a['value_id'])}" for a in dec["alternatives"]]
        lines += ["", "## Decision Outcome", "",
                  f"Chosen option: \"{chosen['label']}\"{_ids(chosen['value_id'])}.", "", dec["rationale"],
                  "", "### Consequences", ""]
        lines += [f"* {c}" for c in dec["consequences"]] or ["* (none stated)"]
        lines += ["", "## Pros and Cons of the Options", ""]
        for a in dec["alternatives"]:
            lines += [f"### {a['label']}", ""]
            lines += [f"* Good, because {x}" for x in a["pros"]] + [f"* Bad, because {x}" for x in a["cons"]]
            if a["citations"]:
                lines.append("* Sources: " + ", ".join(f"`{c}`" for c in a["citations"]))
            lines.append("")
        files[f"{n:04d}-{_slug(title)}.md"] = "\n".join(lines).rstrip() + "\n"
    return files


def render_index(doc: Dict[str, Any], system: str, files: Iterable[str]) -> str:
    """Return the index of a session's ADRs, with the decisions the agent could not ground."""
    lines = [f"# Architecture decisions: {system}", ""]
    lines += [f"* [{adr_title(dec)[0]}]({f})" for dec, f in zip(doc["decisions"], files)]
    if doc.get("uncovered"):
        lines += ["", "## Decisions left open", ""] + [f"* {u}" for u in doc["uncovered"]]
    return "\n".join(lines) + "\n"
