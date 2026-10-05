"""The Taxonomist's coding operations, applied and validated by code (tool-based updates).

In ``taxonomy.edit_mode: tools`` the model never re-emits the taxonomy: it calls
the operations of this editor (add, move, merge, split, rename, relate, remove),
which validate every call against the taxonomy and the batch, apply the valid
ones to a private copy, and log each change with its reason (the operation log).

Rules the editor enforces (plan ``docs/plans/2026-10-02-2134-feat-tool-based-taxonomy-update-plan.md``):

- evidence comes only from the batch's documents, and a new value needs at least one;
- a value with supporting documents is never removed, and a dimension only when empty;
- a split leaves every part with at least two candidate decisions (accepted/rejected);
- values merge only within one dimension and with identical status (cross-stance
  merging stays with value consolidation);
- moved and merged ids stay valid as aliases for the rest of the update, and ids are
  never reused within an update, so an alias never points at a different element.

Errors are returned as ``(False, message)``, never raised, so the model can correct
itself on its next turn.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Callable, Iterable
from typing import Any, get_args

from taxonomy_generator.schemas import DecisionStatus, RelationType
from taxonomy_generator.utils import ensure_unique_ids, value_key

STATUSES = get_args(DecisionStatus)
# Statuses that count as candidate decisions during coding ("mixed" only appears after consolidation).
CODING_CANDIDATE_STATUSES = ("accepted", "rejected")
RELATION_TYPES = get_args(RelationType)


_STOPWORDS = frozenset("a an and as at by for from in into of on or the to under via with without".split())


def _tokens(label: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (label or "").lower()) if len(w) > 1 and w not in _STOPWORDS}


def similar_values(label: str, values: Iterable[dict], threshold: float = 0.34, top: int = 3) -> list[dict]:
    """Values whose labels share words with ``label`` (Jaccard of content words), most similar first.

    A cheap lexical signal for the model, not a judgment: it points at existing options
    a new value may duplicate, so the model can cite evidence or merge instead.
    """
    words = _tokens(label)
    scored = []
    for v in values:
        other = _tokens(v.get("label", ""))
        if words and other:
            score = len(words & other) / len(words | other)
            if score >= threshold:
                scored.append((score, v))
    scored.sort(key=lambda sv: -sv[0])
    return [v for _, v in scored[:top]]


class EditError(ValueError):
    """An invalid operation; its message is returned to the model."""


def _str(args: dict, key: str, required: bool = True) -> str:
    value = args.get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool) and key.endswith("_id"):
        value = str(value)  # models sometimes send ids as numbers (3, 1.2)
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise EditError(f"'{key}' is required")
        return ""
    if not isinstance(value, str):
        raise EditError(f"'{key}' must be a string")
    return value.strip()


def _str_list(args: dict, key: str, min_len: int = 0) -> list[str]:
    value = args.get(key)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise EditError(f"'{key}' must be a list of strings")
    value = list(dict.fromkeys(v.strip() for v in value if v.strip()))
    if len(value) < min_len:
        raise EditError(f"'{key}' needs at least {min_len} entr{'y' if min_len == 1 else 'ies'}")
    return value


class TaxonomyEditor:
    """A working copy of the taxonomy plus the validated operations applied to it."""

    def __init__(self, clusters: Iterable[dict], batch_doc_ids: Iterable[str], review: bool = False):
        """Copy ``clusters``; ``batch_doc_ids`` are the documents evidence may cite; ``review`` relaxes ``set_status``."""
        self.clusters: list[dict] = [copy.deepcopy(c) for c in clusters if isinstance(c, dict)]
        for c in self.clusters:
            c.setdefault("relations", [])
            c.setdefault("values", [])
        self.batch_doc_ids = list(dict.fromkeys(str(d) for d in batch_doc_ids))
        self.review = review
        self.operations: list[dict[str, Any]] = []
        self.rejected: list[dict[str, Any]] = []
        self.cleanup: list[str] = []
        self.uncited: list[str] = []
        self.finished = False
        self.explanation = ""
        self.stop = ""
        self._value_alias: dict[str, str] = {}
        self._dim_alias: dict[str, str] = {}
        self._split: dict[str, list[str]] = {}
        self._retired_values: set[str] = set()
        self._retired_dims: set[str] = set()
        self._created_dims: set[str] = set()
        self._tools: dict[str, Callable[[dict], str]] = {
            "add_value": self._add_value, "add_evidence": self._add_evidence, "move_value": self._move_value,
            "merge_values": self._merge_values, "relabel_value": self._relabel_value,
            "set_status": self._set_status, "remove_value": self._remove_value,
            "add_dimension": self._add_dimension, "rename_dimension": self._rename_dimension,
            "split_dimension": self._split_dimension, "merge_dimensions": self._merge_dimensions,
            "remove_dimension": self._remove_dimension, "add_relation": self._add_relation,
            "remove_relation": self._remove_relation, "finish": self._finish,
        }

    # ------------------------------------------------------------ dispatch

    def apply(self, name: str, args: Any) -> tuple[bool, str]:
        """Validate and apply one operation; return ``(ok, message)`` for the model."""
        tool = self._tools.get(name)
        if tool is None:
            return self._reject(name, args, f"unknown tool '{name}'; available: {', '.join(self._tools)}")
        if not isinstance(args, dict):
            return self._reject(name, args, "arguments must be an object")
        snapshot = self._snapshot()
        try:
            message = tool(args)
        except Exception as exc:  # a rejected call never leaves a half-applied change
            self._restore(snapshot)
            error = str(exc) if isinstance(exc, EditError) else f"internal error ({type(exc).__name__}: {exc})"
            return self._reject(name, args, error)
        if name != "finish":
            self.operations.append({"tool": name, "args": args, "message": message})
        return True, f"ok: {message}"

    _STATE = ("clusters", "_value_alias", "_dim_alias", "_split", "_retired_values", "_retired_dims",
              "_created_dims", "finished", "explanation")

    def _snapshot(self) -> dict[str, Any]:
        return {k: copy.deepcopy(getattr(self, k)) for k in self._STATE}

    def _restore(self, snapshot: dict[str, Any]) -> None:
        for k, v in snapshot.items():
            setattr(self, k, v)

    def uncited_now(self) -> list[str]:
        """Batch documents that no value cites yet."""
        cited = {d for c in self.clusters for v in c["values"] for d in v.get("supporting_doc_ids") or []}
        return [d for d in self.batch_doc_ids if d not in cited]

    def log_rejected(self, name: str, args: Any, error: str) -> None:
        """Record a call that never reached ``apply`` (e.g. unparsable arguments)."""
        self.rejected.append({"tool": name, "args": args, "error": error})

    def _reject(self, name: str, args: Any, error: str) -> tuple[bool, str]:
        self.log_rejected(name, args, error)
        return False, f"error: {error}"

    # ------------------------------------------------------------ lookups

    def resolve_value(self, value_id: str) -> str:
        """Follow move/merge aliases to the value's current id."""
        seen = set()
        while value_id in self._value_alias and value_id not in seen:
            seen.add(value_id)
            value_id = self._value_alias[value_id]
        return value_id

    def _dim(self, dim_id: str) -> dict:
        dim_id = str(dim_id).strip()
        while dim_id in self._dim_alias:
            dim_id = self._dim_alias[dim_id]
        for c in self.clusters:
            if str(c.get("id")) == dim_id:
                return c
        if dim_id in self._split:
            raise EditError(f"dimension {dim_id} was split into {', '.join(self._split[dim_id])}; use those ids")
        known = ", ".join(str(c.get("id")) for c in self.clusters)
        raise EditError(f"unknown dimension id '{dim_id}'; dimensions are: {known}")

    def _value(self, value_id: str) -> tuple[dict, dict]:
        vid = self.resolve_value(str(value_id).strip())
        for c in self.clusters:
            for v in c["values"]:
                if str(v.get("id")) == vid:
                    return c, v
        prefix = vid.split(".", 1)[0]
        dim = next((c for c in self.clusters if str(c.get("id")) == prefix), None)
        if dim is not None:
            ids = ", ".join(str(v.get("id")) for v in dim["values"]) or "none"
            raise EditError(f"unknown value id '{value_id}'; values of dimension {prefix} are: {ids}")
        raise EditError(f"unknown value id '{value_id}'")

    def _check_docs(self, doc_ids: list[str]) -> None:
        outside = [d for d in doc_ids if d not in self.batch_doc_ids]
        if outside:
            raise EditError(f"doc_ids {outside} are not documents of this batch; cite only: "
                            f"{', '.join(self.batch_doc_ids)}")

    def _status(self, args: dict) -> str:
        status = _str(args, "status")
        if status not in STATUSES:
            raise EditError(f"status must be one of {', '.join(STATUSES)}, got '{status}'")
        return status

    @staticmethod
    def _duplicate(dim: dict, label: str, status: str, exclude: dict | None = None) -> dict | None:
        key = value_key(label)
        for v in dim["values"]:
            if v is not exclude and value_key(v.get("label", "")) == key and v.get("status") == status:
                return v
        return None

    def _next_value_id(self, dim: dict) -> str:
        prefix = f"{dim['id']}."
        used = {str(v.get("id")) for v in dim["values"]} | self._retired_values
        n = max((int(i[len(prefix):]) for i in used if i.startswith(prefix) and i[len(prefix):].isdigit()),
                default=0) + 1
        return f"{prefix}{n}"

    def _next_dim_id(self) -> str:
        used = {str(c.get("id")) for c in self.clusters} | self._retired_dims
        return str(max((int(i) for i in used if i.isdigit()), default=0) + 1)

    def _place(self, value: dict, dim: dict) -> str:
        """Append ``value`` to ``dim`` under a fresh id; return the new id (old id becomes an alias)."""
        old = str(value.get("id", ""))
        new = self._next_value_id(dim)
        value["id"], value["dimension_id"] = new, str(dim["id"])
        dim["values"].append(value)
        if old and old != new:
            self._value_alias[old] = new
            self._retired_values.add(old)
        return new

    # ------------------------------------------------------------ values

    def _add_value(self, args: dict) -> str:
        dim = self._dim(_str(args, "dimension_id"))
        label, status = _str(args, "label"), self._status(args)
        doc_ids = _str_list(args, "doc_ids", min_len=1)
        self._check_docs(doc_ids)
        dup = self._duplicate(dim, label, status)
        if dup is not None:
            raise EditError(f"value {dup['id']} '{dup['label']}' ({status}) already exists in dimension "
                            f"{dim['id']}; use add_evidence to cite new documents for it")
        value = {"id": "", "dimension_id": str(dim["id"]), "label": label,
                 "description": _str(args, "description", required=False), "supporting_doc_ids": doc_ids,
                 "status": status}
        similar = similar_values(label, [v for v in dim["values"] if v is not value])
        new = self._place(value, dim)
        message = f"added value {new} '{label}' to dimension {dim['id']}"
        if similar:
            listed = "; ".join(f"{v['id']} '{v.get('label', '')}' ({v.get('status', '')})" for v in similar)
            message += (f". Similar existing values in this dimension: {listed}. If the new value names the same "
                        "option as one of them, merge them with merge_values (same status); for later codes of "
                        "that option use add_evidence instead of add_value")
        return message

    def _add_evidence(self, args: dict) -> str:
        _dim, value = self._value(_str(args, "value_id"))
        doc_ids = _str_list(args, "doc_ids", min_len=1)
        self._check_docs(doc_ids)
        value["supporting_doc_ids"] = list(dict.fromkeys(list(value.get("supporting_doc_ids") or []) + doc_ids))
        return f"value {value['id']} now cites {len(value['supporting_doc_ids'])} documents"

    def _move_value(self, args: dict) -> str:
        source, value = self._value(_str(args, "value_id"))
        target = self._dim(_str(args, "to_dimension_id"))
        if target is source:
            raise EditError(f"value {value['id']} is already in dimension {target['id']}")
        source["values"].remove(value)
        old = value["id"]
        new = self._place(value, target)
        return f"moved value {old} to dimension {target['id']} as {new}"

    def _merge_values(self, args: dict) -> str:
        ids = _str_list(args, "value_ids", min_len=2)
        found = [self._value(i) for i in ids]
        dims = {id(d) for d, _ in found}
        if len(dims) > 1:
            raise EditError("merge_values needs values of one dimension; move them first")
        statuses = {v.get("status") for _, v in found}
        if len(statuses) > 1:
            raise EditError(f"merge_values needs values with identical status, got {sorted(statuses)}; "
                            "values of different status stay separate (consolidation reconciles stances later)")
        dim, keep = found[0]
        if len({id(v) for _, v in found}) < len(found):
            raise EditError("value_ids repeat the same value")
        merged_from = list(keep.get("merged_from") or [])
        docs = list(keep.get("supporting_doc_ids") or [])
        for _, v in found[1:]:
            merged_from.append({"id": v["id"], "label": v.get("label", "")})
            docs.extend(v.get("supporting_doc_ids") or [])
            dim["values"].remove(v)
            self._value_alias[v["id"]] = keep["id"]
            self._retired_values.add(v["id"])
        keep.update(label=_str(args, "label"), description=_str(args, "description", required=False),
                    supporting_doc_ids=list(dict.fromkeys(docs)), merged_from=merged_from)
        return f"merged {', '.join(ids[1:])} into {keep['id']} '{keep['label']}'"

    def _relabel_value(self, args: dict) -> str:
        dim, value = self._value(_str(args, "value_id"))
        label = _str(args, "label")
        dup = self._duplicate(dim, label, value.get("status", ""), exclude=value)
        if dup is not None:
            raise EditError(f"value {dup['id']} already has the label '{dup['label']}' with the same status; "
                            "use merge_values if they are the same option")
        value["label"] = label
        description = _str(args, "description", required=False)
        if description:
            value["description"] = description
        return f"relabeled {value['id']} to '{label}'"

    def _set_status(self, args: dict) -> str:
        _dim, value = self._value(_str(args, "value_id"))
        status = self._status(args)
        reason = _str(args, "reason", required=False)
        cited = {token.strip(".-#") for token in re.findall(r"[A-Za-z0-9_.#-]+", reason)}
        if not self.review and not cited & set(self.batch_doc_ids):
            raise EditError("set_status outside the review needs direct evidence: cite the batch document id "
                            "(e.g. s01_p02) that adopts or declines the option in 'reason'")
        value["status"] = status
        return f"value {value['id']} status set to {status}"

    def _remove_value(self, args: dict) -> str:
        dim, value = self._value(_str(args, "value_id"))
        if value.get("supporting_doc_ids"):
            raise EditError(f"value {value['id']} has supporting documents and cannot be removed during coding; "
                            "move or merge it instead (unsupported content is removed after the loop)")
        dim["values"].remove(value)
        self._retired_values.add(value["id"])
        return f"removed unsupported value {value['id']} '{value.get('label', '')}'"

    # ------------------------------------------------------------ dimensions

    def _check_dim_name(self, name: str, exclude: dict | None = None) -> None:
        key = value_key(name)
        for c in self.clusters:
            if c is not exclude and value_key(c.get("name", "")) == key:
                raise EditError(f"dimension {c['id']} is already named '{c['name']}'")

    def _new_dim(self, name: str, description: str) -> dict:
        dim = {"id": self._next_dim_id(), "name": name, "description": description, "relations": [], "values": []}
        self._created_dims.add(dim["id"])
        return dim

    def _add_dimension(self, args: dict) -> str:
        name = _str(args, "name")
        self._check_dim_name(name)
        dim = self._new_dim(name, _str(args, "description"))
        self.clusters.append(dim)
        return f"added dimension {dim['id']} '{name}' (add values to it in your next turn)"

    def _rename_dimension(self, args: dict) -> str:
        dim = self._dim(_str(args, "dimension_id"))
        name = _str(args, "name")
        self._check_dim_name(name, exclude=dim)
        dim["name"] = name
        description = _str(args, "description", required=False)
        if description:
            dim["description"] = description
        return f"renamed dimension {dim['id']} to '{name}'"

    def _split_dimension(self, args: dict) -> str:
        dim = self._dim(_str(args, "dimension_id"))
        parts = args.get("parts")
        if not isinstance(parts, list) or len(parts) < 2 or not all(isinstance(p, dict) for p in parts):
            raise EditError("split_dimension needs 'parts': a list of at least 2 {name, description, value_ids}")
        by_id = {v["id"]: v for v in dim["values"]}
        assigned: list[list[dict]] = []
        seen: set[str] = set()
        for part in parts:
            values = []
            for raw in _str_list(part, "value_ids"):
                vid = self.resolve_value(raw)
                if vid not in by_id:
                    raise EditError(f"value '{raw}' is not in dimension {dim['id']}")
                if vid in seen:
                    raise EditError(f"value '{raw}' is assigned to more than one part")
                seen.add(vid)
                values.append(by_id[vid])
            assigned.append(values)
        missing = [vid for vid in by_id if vid not in seen]
        if missing:
            raise EditError(f"every value must go to exactly one part; unassigned: {', '.join(missing)}")
        for part, values in zip(parts, assigned):
            candidates = sum(v.get("status") in CODING_CANDIDATE_STATUSES for v in values)
            if candidates < 2:
                raise EditError(f"part '{part.get('name', '?')}' would keep {candidates} candidate decision(s); "
                                "a decision point needs at least 2. Do not split: move the values to the "
                                "dimensions whose questions they answer instead")
        names = [_str(p, "name") for p in parts]
        if len({value_key(n) for n in names}) < len(names):
            raise EditError("part names must differ")
        for n in names:
            self._check_dim_name(n, exclude=dim)

        index = self.clusters.index(dim)
        self.clusters.remove(dim)
        self._retired_dims.add(str(dim["id"]))
        new_dims = []
        for part, values in zip(parts, assigned):
            new = self._new_dim(_str(part, "name"), _str(part, "description", required=False))
            new["relations"] = copy.deepcopy(dim["relations"])
            for v in values:
                self._place(v, new)
            new_dims.append(new)
            # ids of the new dimensions are taken before the next one is created
            self.clusters.insert(index + len(new_dims) - 1, new)
        new_ids = [d["id"] for d in new_dims]
        self._split[str(dim["id"])] = new_ids
        for c in self.clusters:  # incoming relations now point to every part
            rels = []
            for r in c["relations"]:
                if str(r.get("target_id")) == str(dim["id"]):
                    rels.extend({**r, "target_id": nid} for nid in new_ids if nid != c["id"])
                else:
                    rels.append(r)
            c["relations"] = rels
        described = ", ".join(f"{d['id']} '{d['name']}'" for d in new_dims)
        return f"split dimension {dim['id']} into {described}"

    def _merge_dimensions(self, args: dict) -> str:
        ids = _str_list(args, "dimension_ids", min_len=2)
        _str(args, "reason")  # required: the shared question
        dims = [self._dim(i) for i in ids]
        if len({id(d) for d in dims}) < len(dims):
            raise EditError("dimension_ids repeat the same dimension")
        keep, others = dims[0], dims[1:]
        name = _str(args, "name")
        for c in self.clusters:
            if c not in dims and value_key(c.get("name", "")) == value_key(name):
                raise EditError(f"dimension {c['id']} is already named '{c['name']}'")
        merged_ids = {str(d["id"]) for d in dims}
        relations = list(keep["relations"])
        for other in others:
            for v in list(other["values"]):
                self._place(v, keep)
            relations.extend(other["relations"])
            self.clusters.remove(other)
            self._dim_alias[str(other["id"])] = str(keep["id"])
            self._retired_dims.add(str(other["id"]))
        keep.update(name=name, description=_str(args, "description", required=False) or keep.get("description", ""))
        keep["relations"] = self._dedupe([r for r in relations if str(r.get("target_id")) not in merged_ids])
        for c in self.clusters:
            if c is keep:
                continue
            c["relations"] = self._dedupe([{**r, "target_id": str(keep["id"])} if str(r.get("target_id")) in merged_ids
                                           else r for r in c["relations"]])
        return f"merged dimensions {', '.join(ids[1:])} into {keep['id']} '{name}'"

    @staticmethod
    def _dedupe(relations: list[dict]) -> list[dict]:
        seen, out = set(), []
        for r in relations:
            key = (str(r.get("target_id")), r.get("type"))
            if key not in seen:
                seen.add(key)
                out.append(r)
        return out

    def _remove_dimension(self, args: dict) -> str:
        dim = self._dim(_str(args, "dimension_id"))
        if dim["values"]:
            raise EditError(f"dimension {dim['id']} still has values; move them first")
        self.clusters.remove(dim)
        self._retired_dims.add(str(dim["id"]))
        for c in self.clusters:
            c["relations"] = [r for r in c["relations"] if str(r.get("target_id")) != str(dim["id"])]
        return f"removed empty dimension {dim['id']} '{dim.get('name', '')}'"

    # ------------------------------------------------------------ relations and control

    def _add_relation(self, args: dict) -> str:
        source, target = self._dim(_str(args, "source_id")), self._dim(_str(args, "target_id"))
        if source is target:
            raise EditError("a relation needs two different dimensions")
        rtype = _str(args, "type")
        if rtype not in RELATION_TYPES:
            raise EditError(f"relation type must be one of {', '.join(RELATION_TYPES)}, got '{rtype}'")
        if any(str(r.get("target_id")) == str(target["id"]) and r.get("type") == rtype for r in source["relations"]):
            raise EditError(f"relation {source['id']} -{rtype}-> {target['id']} already exists")
        source["relations"].append({"target_id": str(target["id"]), "type": rtype,
                                    "rationale": _str(args, "rationale", required=False)})
        return f"added relation {source['id']} -{rtype}-> {target['id']}"

    def _remove_relation(self, args: dict) -> str:
        source, target = self._dim(_str(args, "source_id")), self._dim(_str(args, "target_id"))
        kept = [r for r in source["relations"] if str(r.get("target_id")) != str(target["id"])]
        if len(kept) == len(source["relations"]):
            raise EditError(f"no relation from {source['id']} to {target['id']}")
        source["relations"] = kept
        return f"removed relation(s) {source['id']} -> {target['id']}"

    def _finish(self, args: dict) -> str:
        self.explanation = _str(args, "explanation")
        self.finished = True
        return "update finished"

    # ------------------------------------------------------------ result

    def result(self) -> list[dict]:
        """Return the edited taxonomy after the consistency checks (notes in ``cleanup``)."""
        self.cleanup = []
        clusters = []
        for c in self.clusters:
            if not c["values"] and c["id"] in self._created_dims:
                self.cleanup.append(f"dropped dimension {c['id']} '{c.get('name', '')}' created in this update "
                                    "but left empty")
                continue
            clusters.append(c)
        ids = {str(c["id"]) for c in clusters}
        for c in clusters:
            kept = []
            for r in c["relations"]:
                if str(r.get("target_id")) in ids and str(r.get("target_id")) != str(c["id"]):
                    kept.append(r)
                else:
                    self.cleanup.append(f"dropped relation {c['id']} -> {r.get('target_id')} (target missing)")
            c["relations"] = kept
            for v in c["values"]:
                v["dimension_id"] = str(c["id"])
        fixed, changes = ensure_unique_ids(clusters)
        self.cleanup.extend(changes)
        cited = {d for c in fixed for v in c.get("values") or [] for d in v.get("supporting_doc_ids") or []}
        self.uncited = [d for d in self.batch_doc_ids if d not in cited]
        return fixed

    def summary(self) -> dict[str, Any]:
        """Return the operation-log entry of this update (without iteration and node)."""
        return {"operations": self.operations, "rejected": self.rejected, "cleanup": self.cleanup,
                "uncited": self.uncited, "explanation": self.explanation, "finished": self.finished,
                "stop": self.stop}
