"""``ddspace point``: interpret one combination of values (a design point) without changing anything.

The checks come from ``query.point`` (no LLM). The description is the wiki's stored one when the wiki already
has a design point with exactly these values and that description names its trade-off; otherwise one LLM call
writes it on the fly, with the prompt and model of the wiki's design-point descriptions. Every description ends
with the point's trade-off ("Trade-off: ..."): what the combination gains and gives up.

Without a space (``--no-space``) the values are the agent's own ``Dimension: Value`` names: there is nothing to
check, and the same prompt describes them, told they were named without a space. The model is ``--model`` or
``DDSPACE_POINT_MODEL``. Nothing is stored: not in the run, the wiki or the design space.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Optional

from delvedspace.workspace import read_json
from taxonomy_generator.wiki import llm_texts
from taxonomy_generator.wiki import query as q

GENERATED_NOTE = "Generated for this request; not stored and not part of the design space."
NAMED_NOTE = "Generated for this request from the agent's own names; there is no design space."
MODEL_ENV = "DDSPACE_POINT_MODEL"


class PointError(Exception):
    """No model to describe the point with."""


def model_for(graph_path: Path, override: Optional[str] = None) -> str:
    """The model that wrote the wiki's descriptions (``raw/run.json``), unless ``override`` names one."""
    if override:
        return override
    built = read_json(Path(graph_path).parent / "run.json", {})
    name = str((built.get("models") or {}).get("generation_llm") or "")
    if not name:
        raise PointError("No model recorded for this wiki (raw/run.json); pass --model provider/name.")
    return name


def _load_env(graph_path: Path) -> None:
    """Read the workspace's .env (the export folder's parent of raw/), for the API key."""
    from dotenv import load_dotenv

    env = Path(graph_path).resolve().parent.parent / ".env"
    if env.is_file():
        load_dotenv(env)


def describe(graph: q.Graph, info: Dict[str, Any], model_name: str, model: Any = None) -> str:
    """One LLM call: the wiki's design-point description for the values in ``info`` (``query.point``)."""
    if model is None:
        from taxonomy_generator.utils import load_chat_model

        model = load_chat_model(model_name)
    slot = {"values": [{"dimension_id": v["dimension_id"], "dimension": v["dimension"], "label": v["label"],
                        "description": v["description"], "status": v["status"]} for v in info["values"]]}
    dims = {v["dimension_id"]: {"description": v["dimension_description"]} for v in info["values"]}
    return asyncio.run(llm_texts.describe(model, slot, dims, str(graph.get("name") or "")))


def point(graph_path: Path, refs, *, llm: bool = True, model_override: Optional[str] = None,
          model: Any = None) -> Dict[str, Any]:
    """Return ``query.point`` plus a description: stored, generated now (not stored), or none with ``llm=False``."""
    graph = q.load(graph_path)
    info = q.point(graph, refs)
    if llm and info["description"] and llm_texts.TRADEOFF_MARK not in info["description"]:
        info["description"] = None  # stored before descriptions named their trade-off: describe it again
    if info["description"]:
        info["description_source"] = "stored"
    elif llm:
        name = model_override or ""
        if model is None:  # ``model`` is given in tests
            name = model_for(graph_path, model_override)
            _load_env(graph_path)
        info["description"] = describe(graph, info, name, model)
        info["description_source"] = "generated"
        info["model"] = name or None
        info["note"] = GENERATED_NOTE
    else:
        info["description_source"] = None
    return info


def named_point(refs, *, domain: str = "", llm: bool = True, model_override: Optional[str] = None,
                model: Any = None) -> Dict[str, Any]:
    """Describe a zero-shot design point: ``Dimension: Value`` names, one value per dimension, no space.

    Raises ``q.QueryError`` for a name that is not ``Dimension: Value`` or a second value for one dimension.
    """
    values, seen = [], {}
    for ref in refs:
        v = q.label_node(ref, ["value"])
        if v is None:
            raise q.QueryError(f"'{ref}' is not a 'Dimension: Value' name (without a space, values are named so)")
        if v["dimension_id"] in seen:
            raise q.QueryError(f"'{v['id']}' is a second value for '{v['dimension']}' (the first is "
                               f"'{seen[v['dimension_id']]}'): a design point takes one value per dimension")
        seen[v["dimension_id"]] = v["id"]
        values.append({"id": v["id"], "dimension_id": v["dimension_id"], "dimension": v["dimension"],
                       "label": v["label"]})
    info: Dict[str, Any] = {"values": values, "space": None, "description": None, "description_source": None}
    if not llm:
        return info
    name = model_override or os.environ.get(MODEL_ENV, "")
    if model is None:  # ``model`` is given in tests
        if not name:
            raise PointError(f"Without a space there is no wiki model: pass --model provider/name or set {MODEL_ENV}.")
        from dotenv import load_dotenv
        from taxonomy_generator.utils import load_chat_model

        load_dotenv(Path.cwd() / ".env")
        model = load_chat_model(name)
    info["description"] = asyncio.run(llm_texts.describe(model, {"values": values}, {}, domain, named=True))
    info.update(description_source="generated", model=name or None, note=NAMED_NOTE)
    return info
