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
from typing import Any, Dict, Iterable, List, Optional

import yaml

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "design.schema.json"
PROMPT = HERE / "prompt.md"
BRIEFS = HERE / "briefs.yaml"
SPACE_CONDITIONS = ("M", "E")              # the conditions with a design space (N has none)
MANIFEST_COPY = "study-manifest.json"      # the input manifest, as copied into each workspace
_TYPES = {"object": dict, "array": list, "string": str, "null": type(None), "number": (int, float), "integer": int,
          "boolean": bool}
_KEY = re.compile(r"sk-[A-Za-z0-9_\-]{12,}")


def schema() -> Dict[str, Any]:
    """Return the design schema."""
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


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
