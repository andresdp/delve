"""Relations between dimensions: one shared table of types, reading sentences and checks.

A relation links two dimensions and always reads left to right as one sentence,
``<source> <verb> <target>`` (e.g. "Training requires Data Profiling to be decided
first"). The same table feeds the schema and tool descriptions, the prompts, the
editor's validation, the wiki and the reports, so the wording never diverges.

Models tend to read "A -> B" as "A relates to B" and then argue in either direction.
Two mechanisms keep the direction right:

- every new relation carries a ``reading`` sentence that :func:`check_reading`
  compares with the type and the two dimension names (names in the right order,
  the type's verb between them);
- :func:`relation_problem` rejects opposite pairs, cycles of ``requires``,
  duplicates and relations beyond a per-dimension cap.

:func:`clean_relations` applies the same rules to a whole taxonomy: rewrite-mode
output, merged dimensions, and saved runs that use the legacy type names
(``precondition``, ``consequence``, ``co_occurring``).
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RelationKind:
    """One relation type: how it reads, which words carry its meaning, and whether it has a direction."""

    name: str
    template: str  # "{a}" = source dimension, "{b}" = target dimension
    verbs: tuple[str, ...]  # normalized words, at least one of which a reading must contain
    directed: bool
    meaning: str


RELATION_KINDS: dict[str, RelationKind] = {
    k.name: k for k in (
        RelationKind("requires", "{a} requires {b} to be decided first", ("requires", "require"), True,
                     "the source only applies once a choice has been made on the target"),
        RelationKind("affects", "Choices on {a} affect the outcomes of {b}", ("affect", "affects"), True,
                     "choices on the source change the results, costs or risks seen on the target"),
        RelationKind("constrains", "Choices on {a} limit the options available on {b}",
                     ("limit", "limits", "constrain", "constrains"), True,
                     "a choice on the source rules out or restricts some choices on the target"),
        RelationKind("co_occurs_with", "{a} and {b} are usually decided together", ("together",), False,
                     "the sources decide both together, but neither causes or requires the other"),
        RelationKind("refines", "{a} is a sub-decision of {b}", ("sub decision", "subdecision"), True,
                     "the source is a narrower decision that only makes sense within the target"),
    )
}
RELATION_TYPES: tuple[str, ...] = tuple(RELATION_KINDS)
DEFAULT_RELATION_TYPES: tuple[str, ...] = ("requires", "affects", "constrains", "co_occurs_with")
LEGACY_RELATION_TYPES = {"precondition": "requires", "consequence": "affects", "co_occurring": "co_occurs_with"}

# Field descriptions shared by the schema (rewrite mode) and the add_relation tool.
TYPE_DESCRIPTION = "; ".join(
    f"{k.name}: \"{k.template.format(a='source', b='target')}\"" for k in RELATION_KINDS.values()
) + f". Types other than {', '.join(DEFAULT_RELATION_TYPES)} may be disabled."
READING_DESCRIPTION = (
    "Write this first: the relation as one sentence with the two real dimension names, the source first, in the "
    "form given for its type (e.g. 'Model Serving Strategy requires Model Packaging Format to be decided first'). "
    "It must be true for the use case exactly as written; if it only holds the other way, swap source and target."
)

_STOPWORDS = {"a", "an", "and", "the", "of", "on", "for", "to", "in", "or", "with", "by", "vs", "via"}


def normalize_type(rtype: object) -> str | None:
    """Return the current name of a relation type (legacy names mapped), or ``None`` when it is not one."""
    name = str(rtype or "").strip()
    name = LEGACY_RELATION_TYPES.get(name, name)
    return name if name in RELATION_KINDS else None


def display_type(rtype: object) -> str | None:
    """Return the current name of a relation type, or the stored value when it is not a known type."""
    return normalize_type(rtype) or (str(rtype) if rtype else None)


def is_directed(rtype: object) -> bool:
    """Return whether a relation type has a direction (unknown types are treated as directed)."""
    kind = RELATION_KINDS.get(normalize_type(rtype) or "")
    return kind.directed if kind else True


def canonical_ends(rtype: object, source_id: str, target_id: str) -> tuple[str, str]:
    """Return ``(source, target)`` as stored: an undirected relation goes on the dimension with the lower id."""
    if not is_directed(rtype) and id_order(target_id) < id_order(source_id):
        return target_id, source_id
    return source_id, target_id


def render_reading(source_name: str, rtype: str, target_name: str) -> str:
    """Return the canonical reading sentence of a relation."""
    return RELATION_KINDS[normalize_type(rtype) or rtype].template.format(a=source_name, b=target_name)


def _tokens(text: str) -> list[str]:
    text = str(text or "").lower().replace("&", " and ").replace("-", " ")
    return re.sub(r"[^a-z0-9]+", " ", text).split()


def _find(sub: list[str], seq: list[str]) -> int:
    for i in range(len(seq) - len(sub) + 1):
        if seq[i:i + len(sub)] == sub:
            return i
    return -1


def _position(name: str, other: str, words: list[str]) -> float | None:
    """Where ``name`` appears among ``words``: exact match, else most of its distinctive words; ``None`` if absent."""
    name_words = _tokens(name)
    if name_words and (start := _find(name_words, words)) >= 0:
        return float(start)
    significant = [w for w in name_words if w not in _STOPWORDS and len(w) > 2]
    other_words = set(_tokens(other))
    distinctive = [w for w in significant if w not in other_words] or significant
    found = [words.index(w) for w in distinctive if w in words]
    if not distinctive or len(found) < max(1, round(0.6 * len(distinctive))):
        return None
    return sum(found) / len(found)


def _verb_positions(rtype: str, words: list[str]) -> list[int]:
    positions = []
    for verb in RELATION_KINDS[rtype].verbs:
        verb_words = verb.split()
        positions += [i for i in range(len(words)) if words[i:i + len(verb_words)] == verb_words]
    return positions


def check_reading(reading: str, source_name: str, target_name: str, rtype: str) -> str | None:
    """``None`` when ``reading`` states the relation ``source -rtype-> target``; otherwise why it does not."""
    rtype = normalize_type(rtype) or rtype
    if rtype not in RELATION_KINDS:
        return f"unknown relation type '{rtype}'"
    words = _tokens(reading)
    src, tgt = _position(source_name, target_name, words), _position(target_name, source_name, words)
    if src is None or tgt is None:
        missing = " and ".join(f"'{n}'" for n, p in ((source_name, src), (target_name, tgt)) if p is None)
        return f"the reading does not name {missing}"
    verbs = _verb_positions(rtype, words)
    if not verbs:
        return f"the reading does not use the wording of '{rtype}'"
    if not RELATION_KINDS[rtype].directed:
        return None
    if any(src < v < tgt for v in verbs):
        return None
    if any(tgt < v < src for v in verbs):
        return "the reading states the reverse direction: swap source and target, or rewrite the sentence"
    return f"the reading must put '{source_name}' before the wording of '{rtype}' and '{target_name}' after it"


def id_order(dim_id: str) -> tuple:
    """Sort key of dimension ids (numeric ids by value): the lower one stores an undirected relation."""
    return (0, int(dim_id), "") if dim_id.isdigit() else (1, 0, dim_id)


def _by_id(clusters: Iterable[dict]) -> dict[str, dict]:
    return {str(c.get("id")): c for c in clusters if isinstance(c, dict)}


def _stored(dims: dict[str, dict], dim_id: str) -> list[dict]:
    return [r for r in dims.get(dim_id, {}).get("relations") or [] if isinstance(r, dict)]


def _has(dims: dict[str, dict], source: str, target: str, rtype: str) -> bool:
    return any(str(r.get("target_id")) == target and normalize_type(r.get("type")) == rtype
               for r in _stored(dims, source))


def _reaches(dims: dict[str, dict], start: str, goal: str, rtype: str) -> bool:
    seen, stack = set(), [start]
    while stack:
        node = stack.pop()
        if node == goal:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack += [str(r.get("target_id")) for r in _stored(dims, node) if normalize_type(r.get("type")) == rtype]
    return False


def relation_problem(clusters: Iterable[dict], source_id: str, target_id: str, rtype: str, reading: str, *,
                     allowed: Iterable[str] = DEFAULT_RELATION_TYPES, check: bool = True,
                     max_per_dimension: int | None = None) -> str | None:
    """Why ``source -rtype-> target`` cannot be added to ``clusters``, or ``None`` when it can.

    ``check`` compares ``reading`` with the type and names; ``max_per_dimension`` caps the
    relations stored on the source (``None`` = no cap).
    """
    return _problem(_by_id(clusters), source_id, target_id, rtype, reading, allowed=allowed, check=check,
                    max_per_dimension=max_per_dimension)


def _problem(dims: dict[str, dict], source_id: str, target_id: str, rtype: str, reading: str, *,
             allowed: Iterable[str], check: bool, max_per_dimension: int | None) -> str | None:
    source, target = str(source_id), str(target_id)
    for dim_id in (source, target):
        if dim_id not in dims:
            return f"unknown dimension '{dim_id}'"
    if source == target:
        return "a relation needs two different dimensions"
    allowed = tuple(allowed)
    if rtype not in allowed:
        return f"relation type must be one of {', '.join(allowed)}, got '{rtype}'"
    kind = RELATION_KINDS[rtype]
    if _has(dims, source, target, rtype) or (not kind.directed and _has(dims, target, source, rtype)):
        return f"relation {source} -{rtype}-> {target} already exists"
    if kind.directed and _has(dims, target, source, rtype):
        return (f"the opposite relation {target} -{rtype}-> {source} exists; two dimensions cannot "
                f"'{rtype}' each other: keep the direction the sources support")
    if rtype == "requires" and _reaches(dims, target, source, rtype):
        return f"{source} -requires-> {target} would create a cycle of 'requires'"
    stored = _stored(dims, source)
    if max_per_dimension is not None and len(stored) >= max_per_dimension:
        return (f"dimension {source} already has {len(stored)} relations (at most {max_per_dimension} per "
                "dimension); keep only the strongest: remove a weaker one first")
    if check:
        names = (str(dims[source].get("name", source)), str(dims[target].get("name", target)))
        problem = check_reading(reading, names[0], names[1], rtype)
        if problem:
            return f"{problem}. Write it as: '{render_reading(names[0], rtype, names[1])}'"
    return None


def clean_relations(clusters: Iterable[dict], *, allowed: Iterable[str] = RELATION_TYPES, check: bool = False,
                    max_per_dimension: int | None = None) -> tuple[list[dict], list[dict]]:
    """Return a copy of ``clusters`` whose relations follow the rules, plus the relations dropped and why.

    Legacy type names are mapped; ``co_occurs_with`` is stored once per pair, on the dimension
    with the lower id; relations are kept in order while each one passes :func:`relation_problem`
    against those kept so far; a missing ``reading`` is filled with the canonical sentence.
    """
    result = [copy.deepcopy(c) for c in clusters if isinstance(c, dict)]
    pending = [(str(c.get("id")), list(c.get("relations") or [])) for c in result]
    for c in result:
        c["relations"] = []
    dims, dropped, allowed = _by_id(result), [], tuple(allowed)
    for source, relations in pending:
        for rel in relations:
            if not isinstance(rel, dict):
                continue
            rtype, src, tgt = normalize_type(rel.get("type")), source, str(rel.get("target_id"))
            reason = None if rtype else f"unknown relation type '{rel.get('type')}'"
            if rtype and tgt in dims:
                src, tgt = canonical_ends(rtype, src, tgt)
            reading = str(rel.get("reading") or "")
            reason = reason or _problem(dims, src, tgt, rtype, reading, allowed=allowed, check=check,
                                        max_per_dimension=max_per_dimension)
            if reason:
                dropped.append({"source_id": source, "target_id": str(rel.get("target_id")),
                                "type": rel.get("type"), "reason": reason})
                continue
            if not reading:
                reading = render_reading(str(dims[src].get("name", src)), rtype, str(dims[tgt].get("name", tgt)))
            dims[src]["relations"].append({**rel, "target_id": tgt, "type": rtype, "reading": reading})
    return result, dropped


def relation_sentence(relation: dict, source_name: str, target_name: str) -> str:
    """How to show a stored relation: its reading sentence from the current names (legacy types mapped).

    The stored ``reading`` is kept as the model wrote it when the relation was created; display
    sentences are rendered from the type and the current names, so renames never leave them stale.
    An unknown type falls back to "source <type> target".
    """
    rtype = normalize_type(relation.get("type"))
    if rtype is None:
        return f"{source_name} {relation.get('type') or 'related to'} {target_name}"
    return render_reading(source_name, rtype, target_name)


def dropped_note(dropped: dict) -> str:
    """One log line for a relation :func:`clean_relations` dropped."""
    return (f"dropped relation {dropped['source_id']} -{dropped['type']}-> {dropped['target_id']}: "
            f"{dropped['reason']}")


def relation_guide(types: Iterable[str] = DEFAULT_RELATION_TYPES) -> str:
    """Return the prompt block that explains relation types, their reading sentences and the rules."""
    rows = "\n".join(
        f"| `{t}` | {RELATION_KINDS[t].template.format(a='A', b='B')} | {RELATION_KINDS[t].meaning} |"
        for t in types)
    return (
        "Relations between dimensions. A relation goes **from** a source dimension A **to** a target dimension B "
        "and always reads left to right as one sentence:\n\n"
        "| Type | Reading (A = source, B = target) | Meaning |\n|---|---|---|\n" + rows + "\n\n"
        "- **Write the `reading` first**: the sentence above with the two real dimension names, source first. It "
        "must be true for the use case exactly as written. If it only holds the other way round, swap source and "
        "target.\n"
        "- Correct: \"Model Serving Strategy requires Model Packaging Format to be decided first\" (serving is "
        "chosen after packaging) is stored as source = Model Serving Strategy, target = Model Packaging Format, "
        "type `requires`.\n"
        "- Reversed (wrong): the same pair stored as source = Model Packaging Format, target = Model Serving "
        "Strategy, `requires`, with the rationale \"packaging must be settled before serving\": the rationale "
        "argues the opposite of the stored direction. Fix it by swapping source and target.\n"
        "- Only a few relations per dimension: keep the interactions the sources actually discuss. A relation that "
        "only says two topics are related is not a relation; extra relations beyond the cap are rejected.\n"
        "- Never relate two dimensions both ways with the same directed type, and never build a cycle of "
        "`requires`.\n"
        "- Use `co_occurs_with` only when the sources show the two decisions being made together."
    )
