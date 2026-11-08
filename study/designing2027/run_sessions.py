#!/usr/bin/env python3
r"""Run the Designing 2027 sessions: one ``codex exec`` per case, condition and repetition, each in a fresh copy.

A case (``cases/<folder>/``, see ``cases/README.md``) is a problem, plus a solution for an explain case. In
each session a coding agent uses the ``ddspace-search`` or ``ddspace-explain`` skill and writes one rationale
file, ``./rationale/<case>.json``, in one of three conditions:

| Condition | The work copy | The skill variant |
|---|---|---|
| M | the mined C1 space (a workspace from ``study/cain2027/build_workspaces.py``) | with a space |
| E | the expert C1 space (the same builder) | with a space |
| N | an empty folder; ``ddspace`` is on the PATH, so only the structural check runs (KTD3) | no space |

The CAIN runner's controls are reused as they are (private ``CODEX_HOME``, pinned model, web search off, the
workspace manifest, the event parsing and redaction; ``study/cain2027/`` is not changed). As in CAIN, only M and
E sessions get sandbox network access and the study key (``STUDY_OPENAI_API_KEY``, passed as ``OPENAI_API_KEY``)
for the description ``ddspace point`` generates; N gets neither. The summary counts any other network use, and
web search is disabled in every session. After each session the runner keeps, under ``--results``:

- ``rationale/<session>.json``: the agent's final rationale file (the home folder and keys redacted);
- ``summaries/<session>.json``: an allow-listed summary of the event log, the final ``ddspace rationale check``
  (ok and problem codes), the number of check runs, a fabrication audit (ids in the file that no command
  returned), for explain the possible retrieval misses, and the explainer's path;
- ``explainers/<session>/``: the explainer, from ``ddspace rationale build --out`` (every condition); for M and
  E its wiki links point into ``--workspaces/<condition>``, which outlives the session's work copy.

A session is done when its rationale file is kept and its summary says ``status: ok``; any other session
(failed, or with an unreadable summary) runs again on the next invocation.

``--skills-via files`` writes the skill to ``.agents/skills/<name>/SKILL.md`` in the work copy (Codex reads
repository skills there); ``--skills-via prompt`` appends it to the prompt instead. A smoke test decides which,
before the study (plan U5).

Usage::

    STUDY_OPENAI_API_KEY=... python study/designing2027/run_sessions.py --workspaces <folder with M and E> \\
        --scratch <folder> --model <codex model> [--cases kv-store,feed] [--conditions M,E,N] [--reps 2] \\
        [--skills-via files]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import yaml

HERE = Path(__file__).resolve().parent
CAIN = HERE.parent / "cain2027"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module              # dataclasses look their module up while the class is built
    spec.loader.exec_module(module)
    return module


cain = sys.modules.get("cain2027_run_sessions") or _import("cain2027_run_sessions", CAIN / "run_sessions.py")
design = cain.design                         # redact, sha256, results-folder names

from delvedspace import agent, rationale  # noqa: E402
from taxonomy_generator.wiki import query as q  # noqa: E402

RESULTS = HERE / "results"
CASES = HERE / "cases"
PROMPT = HERE / "prompt.md"
CONDITIONS = ("M", "E", "N")
SPACE_CONDITIONS = cain.SPACE_CONDITIONS      # M and E
MODES = rationale.MODES
SKILL = {name.removeprefix("ddspace-"): name for name in agent.SKILLS}  # mode -> skill
SKILLS_VIA = ("files", "prompt")
TIMEOUT = cain.TIMEOUT
DDSPACE_TIMEOUT = 300                         # seconds for the runner's own check and build
_CASE_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_WORD = re.compile(r"[A-Za-z0-9]+")
# Words too common to be worth a graph search in the retrieval-miss lookup.
STOPWORDS = frozenset("""a an and are as at be by for from how in into is it of on or the to via what when where
which with without its their this that these those each per use using based between""".split())
MIN_WORD = 3


@dataclass(frozen=True)
class Session:
    """One agent session: a case, a condition (M, E or N) and a repetition number."""

    case: str
    condition: str
    rep: int

    @property
    def id(self) -> str:
        """Return the session id, e.g. ``kv-store-M-r1``."""
        return f"{self.case}-{self.condition}-r{self.rep}"


# ---------------------------------------------------------------- cases and the plan


def load_cases(folder: Path = CASES) -> List[Dict[str, Any]]:
    """Return the cases under ``folder`` (``id``, ``mode``, ``dir``), sorted by folder name."""
    cases, seen = [], set()
    for d in sorted(p for p in Path(folder).iterdir() if p.is_dir()):
        meta_path = d / "case.yaml"
        if not meta_path.is_file():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        case_id, mode = str(meta.get("id") or ""), meta.get("mode")
        if not _CASE_ID.match(case_id):
            raise ValueError(f"{meta_path}: id {case_id!r}: use lowercase letters, digits and hyphens")
        if mode not in MODES:
            raise ValueError(f"{meta_path}: mode {mode!r}: use one of {', '.join(MODES)}")
        if case_id in seen:
            raise ValueError(f"{meta_path}: duplicate case id {case_id!r}")
        if not (d / "problem.md").is_file():
            raise ValueError(f"{d}: no problem.md")
        if mode == "explain" and not (d / "solution.md").is_file():
            raise ValueError(f"{d}: an explain case needs solution.md")
        seen.add(case_id)
        cases.append({"id": case_id, "mode": mode, "dir": d})
    return cases


def plan(cases: List[Mapping[str, Any]], conditions: Iterable[str], reps: int) -> List[Session]:
    """All sessions, case by case (so a partial run still covers every condition of the first cases)."""
    conditions = list(conditions)
    return [Session(c["id"], cond, r) for c in cases for r in range(1, reps + 1) for cond in conditions]


def kept_file(results: Path, session: Session) -> Path:
    """Where a session's final rationale file is kept."""
    return results / "rationale" / f"{session.id}.json"


def read_summary(path: Path) -> Optional[Dict[str, Any]]:
    """Return a session summary, or None when it is missing, unreadable or not a JSON object."""
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):            # UnicodeDecodeError and JSONDecodeError are ValueErrors
        return None
    return rec if isinstance(rec, dict) else None


def done(results: Path, session: Session) -> bool:
    """Whether a session is finished: its rationale file is kept and its summary says ``status: ok``."""
    if not kept_file(results, session).is_file():
        return False
    rec = read_summary(results / "summaries" / f"{session.id}.json")
    return rec is not None and rec.get("status") == "ok"


def pending(sessions: List[Session], results: Path = RESULTS) -> List[Session]:
    """Return the sessions that are not done (a failed session runs again, even if it left a file)."""
    return [s for s in sessions if not done(results, s)]


# ---------------------------------------------------------------- the prompt and the skill


def prompt_sections(prompt: Path = PROMPT) -> Dict[str, str]:
    """Return the ``## <name>`` sections of the prompt file (lowercase names; text before the first is a note)."""
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in prompt.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() + "\n" for k, v in sections.items()}


def prompt_text(prompt: Path, case: Mapping[str, Any], condition: str, extra: str = "") -> str:
    """Return the prompt for one session: the case's mode section with the case id and the condition's space note.

    ``extra`` (the skill text, with ``--skills-via prompt``) is appended after it.
    """
    sections = prompt_sections(prompt)
    note = sections["space" if condition in SPACE_CONDITIONS else "no space"].strip()
    text = sections[case["mode"]].replace("{case}", case["id"]).replace("{space}", note)
    return text.rstrip("\n") + "\n" + (f"\n{extra}" if extra else "")


def skills_sha256() -> str:
    """SHA-256 over every skill file a session can receive (both skills, each SKILL.md and space reference)."""
    digest = hashlib.sha256()
    for name in agent.SKILLS:
        for rel, text in agent.skill_files(name, space=True).items():
            digest.update(f"{name}/{rel}\n".encode("utf-8") + text.encode("utf-8"))
    return digest.hexdigest()


def deliver_skill(workdir: Path, mode: str, condition: str, via: str) -> str:
    """Give the session its skill; return the text to append to the prompt (empty with ``via="files"``).

    Every condition gets the same ``SKILL.md``; M and E also get the space reference
    (``references/design-space.md``), N does not. ``files`` writes them where Codex reads repository skills
    (``.agents/skills/<name>/``); ``prompt`` returns them instead, the reference after the skill.
    """
    if via not in SKILLS_VIA:
        raise ValueError(f"skills via {via!r}: use one of {', '.join(SKILLS_VIA)}")
    name = SKILL[mode]
    files = agent.skill_files(name, space=condition in SPACE_CONDITIONS)
    if via == "prompt":
        parts = [f"The `{name}` skill follows (its SKILL.md).\n\n{files['SKILL.md']}"]
        if agent.REFERENCE in files:
            parts.append(f"Its {agent.REFERENCE} follows.\n\n{files[agent.REFERENCE]}")
        return "\n".join(parts)
    for rel, text in files.items():
        path = workdir / ".agents" / "skills" / name / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return ""


def prepare_workdir(session: Session, case: Mapping[str, Any], workspaces: Path, workdir: Path) -> None:
    """Make the session's work copy: the condition's workspace (empty for N), the problem and the solution.

    Skill folders a workspace may hold (from ``ddspace agent setup --skills``) are removed, so the skill the
    runner delivers is the only one a session sees.
    """
    if session.condition in SPACE_CONDITIONS:
        shutil.copytree(workspaces / session.condition, workdir)
    else:
        workdir.mkdir(parents=True)
    for folder in agent.SKILL_DIRS:
        shutil.rmtree(workdir / folder, ignore_errors=True)
    shutil.copyfile(Path(case["dir"]) / "problem.md", workdir / "PROBLEM.md")
    if case["mode"] == "explain":
        shutil.copyfile(Path(case["dir"]) / "solution.md", workdir / "SOLUTION.md")


# ---------------------------------------------------------------- command, controls and environment


def command(session: Session, workdir: Path, last: Path, *, model: str, oss: Optional[str] = None) -> List[str]:
    """Return the ``codex exec`` argv for one session: CAIN's, without ``--output-schema``.

    As in CAIN, M and E get sandbox network access (for ``ddspace point`` descriptions); N does not.
    """
    argv = ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config",
            "-s", "workspace-write", "-m", model, "-o", str(last), "-C", str(workdir), "-c", cain.WEB_SEARCH_OFF]
    if oss:
        argv += ["--oss", "--local-provider", oss]
    for feature in cain.DISABLED_FEATURES:
        argv += ["--disable", feature]
    if session.condition in SPACE_CONDITIONS:
        argv += ["-c", cain.NETWORK_ON, "-c", "shell_environment_policy.ignore_default_excludes=true"]
    return argv + ["-"]   # the prompt comes on stdin


def preflight(session: Session, argv: List[str], workdir: Path, manifest: Path = cain.MANIFEST, *, model: str,
              matching_model: str = "", skill: Optional[str] = None) -> List[str]:
    """Return why the session must not start (empty when every control holds).

    CAIN's checks run as they are, for the session's condition: the pinned model, web search off, network
    access that matches the condition (on for M and E, off for N) and, for M and E, the study manifest in the
    work copy. No matcher judges this study, so ``matching_model`` is empty by default. ``skill`` (with
    ``--skills-via files``) needs its ``SKILL.md`` there.
    """
    problems = cain.preflight(cain.Session(session.case, session.condition, session.rep), argv, workdir, manifest,
                              model=model, matching_model=matching_model)
    if skill and not (workdir / ".agents" / "skills" / skill / "SKILL.md").is_file():
        problems.append(f"the skill file .agents/skills/{skill}/SKILL.md is missing")
    return problems


def _environment(session: Session, codex_home: Path, ddspace_bin: Optional[Path], key: Optional[str] = None,
                 oss: Optional[str] = None) -> Dict[str, str]:
    """Return the session's environment: CAIN's allow-list, ``ddspace`` on the PATH in every condition.

    M and E also get the study key ``key`` as ``OPENAI_API_KEY`` (for ``ddspace point`` descriptions); N never
    gets a key, and the operator's own ``OPENAI_API_KEY`` is never passed on.
    """
    path = [p for p in os.environ.get("PATH", "").split(os.pathsep) if not (Path(p) / "ddspace").exists()]
    env = {k: os.environ[k] for k in cain.SAFE_ENV if k in os.environ}
    if oss:
        env.update({k: v for k, v in os.environ.items() if k.startswith(f"{oss.upper()}_")})
    if ddspace_bin is not None:
        path.insert(0, str(ddspace_bin.parent))
    env.update(CODEX_HOME=str(codex_home), PATH=os.pathsep.join(path))
    if key and session.condition in SPACE_CONDITIONS:
        env["OPENAI_API_KEY"] = key
    return env


def guards(results: Path, *, model: str, prompt: Path, skills_via: str) -> List[str]:
    """Why ``results`` must not take more sessions now: another model, prompt version or skill delivery.

    The checks are CAIN's (``model_mismatch``, ``prompt_mismatch``), done here over :func:`read_summary`, so an
    unreadable summary (a crash while it was written) is skipped: that session is pending and runs again.
    """
    out = []
    prompt_digest, digest = design.sha256(prompt), skills_sha256()
    other, mixed, skills = [], [], []
    for path in sorted((results / "summaries").glob("*.json")):
        rec = read_summary(path)
        if rec is None:
            continue
        if rec.get("model") and rec["model"] != model:
            other.append(path.stem)
        if rec.get("prompt_sha256") and rec["prompt_sha256"] != prompt_digest:
            mixed.append(path.stem)
        if (rec.get("skills_via") and rec["skills_via"] != skills_via) or (
                rec.get("skills_sha256") and rec["skills_sha256"] != digest):
            skills.append(path.stem)
    if other:
        out.append(f"{results.name}/ holds {len(other)} sessions run with another agent model (such as {other[0]}); "
                   f"use another --results folder.")
    if mixed:
        out.append(f"{results.name}/ holds {len(mixed)} sessions run with another version of {prompt.name} "
                   f"(such as {mixed[0]}); move that folder aside first.")
    if skills:
        out.append(f"{results.name}/ holds {len(skills)} sessions run with another skill text or skill delivery "
                   f"(such as {skills[0]}); use another --results folder.")
    return out


# ---------------------------------------------------------------- the event log


def _command_name(args: List[str]) -> str:
    """``query values``, ``rationale check``, ``point``: two words for the commands with subcommands."""
    return " ".join(args[:2]) if args[0] in ("query", "wiki", "agent", "rationale") and len(args) > 1 else args[0]


def summarize(events: List[Dict[str, Any]], *, home: str, secrets: Iterable[str]) -> Dict[str, Any]:
    """Return an allow-listed summary of a session's event log (no free text, paths, user names or keys)."""
    secrets = list(secrets)

    def clean(text: str) -> str:
        return design.redact(text, home, secrets)

    calls: Counter = Counter()
    points, network, web, commands = [], 0, 0, 0
    tokens = {"input": 0, "cached_input": 0, "output": 0, "reasoning": 0}
    complete = False
    for e in events:
        item = e.get("item") or {}
        if e.get("type") == "turn.completed":
            complete = True
            usage = e.get("usage") or {}
            for key, field in (("input", "input_tokens"), ("cached_input", "cached_input_tokens"),
                               ("output", "output_tokens"), ("reasoning", "reasoning_output_tokens")):
                tokens[key] += int(usage.get(field) or 0)
        if e.get("type") != "item.completed":
            continue
        if item.get("type") == "web_search":
            web += 1
        if item.get("type") != "command_execution":
            continue
        commands += 1
        script = cain._inner(str(item.get("command") or ""))
        for args in cain._ddspace_calls(script):
            if not args:
                continue
            calls[_command_name(args)] += 1
            if args[0] == "point":
                points.append(cain._point_event(args, str(item.get("aggregated_output") or ""),
                                                item.get("exit_code") == 0, clean))
        if cain._uses_network(script):
            network += 1
    return {"complete": complete, "commands": commands, "ddspace_calls": dict(calls),
            "check_runs": calls["rationale check"], "build_runs": calls["rationale build"], "points": points,
            "network_commands": network, "web_search": web, "tokens": tokens}


# ---------------------------------------------------------------- fabrication audit


def file_ids(doc: Any) -> List[str]:
    """Return the space ids a rationale file names, in file order: dimensions, values, passages and sources."""
    ids: List[str] = []

    def add(value: Any) -> None:
        if isinstance(value, str) and value.strip() and value not in ids:
            ids.append(value)

    if not rationale.names_space(doc):   # no wiki: the agent's own ids (space.dimensions) are not the space's
        return ids
    for alt in doc.get("alternatives") or []:
        if not isinstance(alt, dict):
            continue
        for key in ("choices", "considered"):
            for c in alt.get(key) or []:
                if isinstance(c, dict):
                    add(c.get("dimension_id"))
                    add(c.get("value_id"))
                    for ev in c.get("evidence") or []:
                        add(ev.get("doc") if isinstance(ev, dict) else None)
        for o in alt.get("open") or []:
            add(o.get("dimension_id") if isinstance(o, dict) else None)
        for r in alt.get("relations") or []:
            if isinstance(r, dict):
                add(r.get("source"))
                add(r.get("target"))
    for step in doc.get("trajectory") or []:          # the design points investigated, with what point reported
        if not isinstance(step, dict):
            continue
        for v in step.get("values") or []:
            add(v)
        point = step.get("point")
        for s in (point.get("attested_by") or []) if isinstance(point, dict) else []:
            add(s.get("id") if isinstance(s, dict) else s)    # a source id, or a source object with its id
    for region in doc.get("regions") or []:
        for v in (region.get("values") or []) if isinstance(region, dict) else []:
            add(v)
    for key, field in (("comparison", "dimension_id"), ("uncovered", "nearest_dimension_id")):
        for item in doc.get(key) or []:
            add(item.get(field) if isinstance(item, dict) else None)
    return ids


def mentions(text: str, ident: str) -> bool:
    """Whether ``text`` names ``ident`` as a whole id (``v:2.1`` is not in ``v:2.10``)."""
    return re.search(rf"(?<![\w:.]){re.escape(ident)}(?![\w]|\.\d)", text) is not None


def _candidates(output: str) -> List[str]:
    """Every id among the ``candidates`` of a ``ddspace rationale check`` JSON output (not its ``resolved``)."""
    try:
        data = json.loads(output[output.index("{"):]) if "{" in output else {}
    except ValueError:
        return []
    found: List[str] = []
    for p in data.get("problems") or [] if isinstance(data, dict) else []:
        for c in p.get("candidates") or [] if isinstance(p, dict) else []:
            if isinstance(c, str):
                found.append(c)
            elif isinstance(c, dict):
                found += [str(c[k]) for k in ("id", "doc", "source", "target") if c.get(k)]
    return found


def fabrication_audit(doc: Any, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check that every id in the final file was returned by a command during the session.

    An id counts as returned when the output of a ``ddspace`` command other than ``ddspace rationale`` names it
    (``query``, ``point``). The rest are reported in three disjoint lists:

    - ``candidate_only``: named only as a candidate in a ``rationale check`` output (the checker suggested it);
    - ``other_output_only``: named only in the output of a command that is not ``ddspace`` (reading
      ``raw/graph.json`` with ``grep``, or printing the agent's own file);
    - ``missing``: named in no command output at all.

    The ``resolved`` list of a check output echoes the file's own ids, so it never counts.
    """
    returned, candidates, other = [], [], []
    for e in events:
        item = e.get("item") or {}
        if e.get("type") != "item.completed" or item.get("type") != "command_execution":
            continue
        output = str(item.get("aggregated_output") or "")
        calls = [a for a in cain._ddspace_calls(cain._inner(str(item.get("command") or ""))) if a]
        if any(a[0] == "rationale" for a in calls):
            candidates += _candidates(output)
        elif calls:
            returned.append(output)
        else:
            other.append(output)
    ids = file_ids(doc)
    out: Dict[str, Any] = {"ids": len(ids), "missing": [], "candidate_only": [], "other_output_only": []}
    for ident in ids:
        if any(mentions(o, ident) for o in returned):
            continue
        if ident in candidates:
            out["candidate_only"].append(ident)
        elif any(mentions(o, ident) for o in other):
            out["other_output_only"].append(ident)
        else:
            out["missing"].append(ident)
    return out


# ---------------------------------------------------------------- retrieval misses


def _words(text: str) -> List[str]:
    words: List[str] = []
    for w in _WORD.findall(text.lower()):
        if len(w) >= MIN_WORD and w not in STOPWORDS and w not in words:
            words.append(w)
    return words


def retrieval_misses(doc: Any, graph: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Return the uncovered items of an explain file that a broader search finds dimensions for.

    For each item, every word of its ``decision`` (stopwords and words under three letters left out) is searched
    as one ``q.search`` keyword among the dimensions. An item with any match is a possible retrieval miss: the
    space may cover the decision although the agent did not map it. ``uncovered`` stays an upper bound on what
    the space lacks; these are leads for a person to read, not verdicts.
    """
    if not isinstance(doc, dict) or doc.get("mode") != "explain":
        return []
    misses = []
    for i, item in enumerate(doc.get("uncovered") or []):
        if not isinstance(item, dict):
            continue
        words = _words(str(item.get("decision") or ""))
        found: Dict[str, Dict[str, Any]] = {}
        for word in words:
            for hit in q.search(graph, word, kind="dimension"):
                match = found.setdefault(hit["id"], {"id": hit["id"], "label": hit.get("label"),
                                                     "match": hit.get("match"), "words": []})
                if hit.get("match") == "label":
                    match["match"] = "label"
                match["words"].append(word)
        if found:
            misses.append({"path": f"/uncovered/{i}", "decision": item.get("decision"),
                           "nearest_dimension_id": item.get("nearest_dimension_id"),
                           "matches": sorted(found.values(), key=lambda m: (m["match"] != "label", m["id"]))})
    return misses


# ---------------------------------------------------------------- after the session


def ddspace_command(ddspace_bin: Optional[Path]) -> List[str]:
    """How the runner itself calls ``ddspace``: the installed script, else this Python's module."""
    return [str(ddspace_bin)] if ddspace_bin is not None and ddspace_bin.is_file() else [
        sys.executable, "-m", "delvedspace"]


def _ddspace(ddspace: Sequence[str], args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(list(ddspace) + args, cwd=str(cwd), capture_output=True, text=True,
                          timeout=DDSPACE_TIMEOUT)


def _last_line(text: str) -> str:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[-1][:300] if lines else ""


def final_check(ddspace: Sequence[str], workdir: Path, file: Path) -> Dict[str, Any]:
    """Run ``ddspace rationale check`` on the final file, in the work copy (where an M or E graph is found)."""
    try:
        proc = _ddspace(ddspace, ["rationale", "check", str(file)], workdir)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": None, "ok": False, "problems": [], "error": f"{type(exc).__name__}: {exc}"}
    out: Dict[str, Any] = {"exit_code": proc.returncode}
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        data = None
    if isinstance(data, dict) and "ok" in data:
        out.update(ok=bool(data["ok"]), graph_sha256=data.get("graph_sha256"),
                   problems=[{"code": p.get("code"), "severity": p.get("severity"), "path": p.get("path")}
                             for p in data.get("problems") or []])
    else:
        error = data.get("error") if isinstance(data, dict) else None
        out.update(ok=False, problems=[], error=str(error or _last_line(proc.stderr) or _last_line(proc.stdout)))
    return out


def build_explainer(ddspace: Sequence[str], workdir: Path, file: Path, results: Path,
                    session: Session, workspaces: Optional[Path] = None) -> Dict[str, Any]:
    """Render the explainer with ``ddspace rationale build --out`` under the results folder (every condition).

    Run in the work copy. For M and E, ``--graph`` names the condition's workspace under ``workspaces`` (the
    same graph the work copy was copied from), so the page's wiki links point into a wiki that outlives the work
    copy, which is deleted after the session; ``links_into`` records it (``--workspaces/<condition>``, no path).
    A missing ``build`` command (or any failure) is recorded, not raised.
    """
    out_dir = results / "explainers" / session.id
    shutil.rmtree(out_dir, ignore_errors=True)
    rec: Dict[str, Any] = {"out": out_dir.relative_to(results).as_posix(), "links_into": None}
    args = ["rationale", "build", str(file), "--out", str(out_dir)]
    if workspaces is not None and session.condition in SPACE_CONDITIONS:
        args += ["--graph", str(Path(workspaces) / session.condition / "raw" / "graph.json")]
        rec["links_into"] = f"--workspaces/{session.condition}"
    try:
        proc = _ddspace(ddspace, args, workdir)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return dict(rec, exit_code=None, error=f"{type(exc).__name__}: {exc}", pages=[])
    rec["exit_code"] = proc.returncode
    if proc.returncode != 0:
        rec["error"] = _last_line(proc.stderr) or _last_line(proc.stdout)
    rec["pages"] = sorted(p.relative_to(results).as_posix() for p in out_dir.rglob("*.html")) if out_dir.is_dir() \
        else []
    return rec


def postflight(summary: Dict[str, Any], session: Session, case: Mapping[str, Any], workdir: Path,
               events: List[Dict[str, Any]], results: Path, *, ddspace: Sequence[str], home: str,
               secrets: Iterable[str], workspaces: Optional[Path] = None) -> Dict[str, Any]:
    """Keep the session's rationale file and check, audit and render it; return the fields for the summary.

    ``problems`` lists why the session does not count: an incomplete log, web search, no rationale file or a
    file that is not UTF-8 JSON. A final check with errors does not fail the session: it is the session's result.
    ``workspaces`` (the persistent M and E workspaces) is where the explainer's wiki links point.
    """
    problems = []
    if not summary["complete"]:
        problems.append("the event log is not complete (no turn.completed)")
    if summary["web_search"]:
        problems.append("the agent used web search")
    rel = f"rationale/{case['id']}.json"
    file = workdir / rel
    if not file.is_file():
        return {"problems": [f"no rationale file: the agent wrote no {rel}"] + problems}
    try:
        text = file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return {"problems": [f"{rel} is not UTF-8: {exc.reason} at byte {exc.start}"] + problems}
    try:
        doc = json.loads(text)
    except ValueError as exc:
        return {"problems": [f"{rel} is not JSON: {exc}"] + problems}
    kept = kept_file(results, session)
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text(design.redact(text, home, list(secrets)), encoding="utf-8")
    rec: Dict[str, Any] = {"problems": problems, "rationale": kept.relative_to(results).as_posix(),
                           "fabrication": fabrication_audit(doc, events)}
    rec["check"] = final_check(ddspace, workdir, Path(rel))
    rec["retrieval_misses"] = None
    if session.condition in SPACE_CONDITIONS and isinstance(doc, dict) and doc.get("mode") == "explain":
        try:
            rec["retrieval_misses"] = retrieval_misses(doc, q.load(workdir / "raw" / "graph.json"))
        except (q.QueryError, OSError, ValueError) as exc:
            rec["retrieval_misses"] = {"error": str(exc)}
    if rec["check"].get("ok"):
        rec["explainer"] = build_explainer(ddspace, workdir, Path(rel), results, session, workspaces)
    else:
        rec["explainer"] = {"skipped": "the final check is not clean"}
    return rec


# ---------------------------------------------------------------- one session


def run(session: Session, case: Mapping[str, Any], workspaces: Path, scratch: Path, *, model: str,
        results: Path = RESULTS, prompt: Path = PROMPT, skills_via: str = "files", keep_raw: bool = False,
        ddspace_bin: Optional[Path] = None, ddspace: Optional[Sequence[str]] = None, timeout: int = TIMEOUT,
        oss: Optional[str] = None, version: Optional[str] = None, key: Optional[str] = None) -> Dict[str, Any]:
    """Run one session; keep its rationale file and summary; return the summary.

    ``key`` is the study key M and E sessions get as ``OPENAI_API_KEY``; it is redacted from what is kept.
    """
    root = scratch / session.id
    shutil.rmtree(root, ignore_errors=True)
    try:
        return _run(session, case, workspaces, root, model=model, results=results, prompt=prompt,
                    skills_via=skills_via, keep_raw=keep_raw, ddspace_bin=ddspace_bin,
                    ddspace=list(ddspace) if ddspace else ddspace_command(ddspace_bin), timeout=timeout, oss=oss,
                    version=version, key=key)
    finally:
        shutil.rmtree(root / "codex-home", ignore_errors=True)     # the copied login never outlives the session
        if not keep_raw:
            shutil.rmtree(root, ignore_errors=True)


def _run(session: Session, case: Mapping[str, Any], workspaces: Path, root: Path, *, model: str, results: Path,
         prompt: Path, skills_via: str, keep_raw: bool, ddspace_bin: Optional[Path], ddspace: List[str],
         timeout: int, oss: Optional[str], version: Optional[str], key: Optional[str]) -> Dict[str, Any]:
    workdir = root / "ws"
    prepare_workdir(session, case, workspaces, workdir)
    extra = deliver_skill(workdir, case["mode"], session.condition, skills_via)
    last = root / "last.txt"
    argv = command(session, workdir, last, model=model, oss=oss)
    argv[0] = shutil.which("codex") or "codex"           # resolved here: the session PATH may not have it
    record: Dict[str, Any] = {
        "session": session.id, "case": session.case, "mode": case["mode"], "condition": session.condition,
        "rep": session.rep, "model": model, "provider": oss or "openai", "codex_version": version,
        "prompt": prompt.name, "prompt_sha256": design.sha256(prompt), "skills_via": skills_via,
        "skill": SKILL[case["mode"]], "skill_variant": "space" if session.condition in SPACE_CONDITIONS else "no space",
        "skills_sha256": skills_sha256(), "started_at": datetime.now().isoformat(timespec="seconds")}
    problems = preflight(session, argv, workdir, model=model,
                         skill=SKILL[case["mode"]] if skills_via == "files" else None)
    if not problems:
        env = _environment(session, cain._codex_home(root), ddspace_bin, key, oss)
        start = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(cain.NATIVE + argv, input=prompt_text(prompt, case, session.condition, extra),
                                  capture_output=True, text=True, env=env, timeout=timeout)
            stdout, stderr, record["exit_code"] = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            record["exit_code"] = None
        record["seconds"] = round(time.monotonic() - start, 1)
        if keep_raw:
            raw = results / "raw"
            raw.mkdir(parents=True, exist_ok=True)
            (raw / f"{session.id}.jsonl").write_text(stdout, encoding="utf-8")
            (raw / f"{session.id}.stderr.txt").write_text(stderr, encoding="utf-8")
        events = cain._events(stdout)
        home = str(Path.home())
        secrets = [key] if key else []
        summary = summarize(events, home=home, secrets=secrets)
        after = postflight(summary, session, case, workdir, events, results, ddspace=ddspace, home=home,
                           secrets=secrets, workspaces=workspaces)
        problems = ([f"timed out after {timeout} s"] if timed_out else []) + after.pop("problems")
        record.update(summary, **after)
    record.update(status="failed" if problems else "ok", problems=problems)
    (results / "summaries").mkdir(parents=True, exist_ok=True)
    (results / "summaries" / f"{session.id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


# ---------------------------------------------------------------- the command line


def results_folder(name: str) -> Path:
    """Return the results folder ``name`` in this study folder (``results`` or ``results-<label>``, as in CAIN)."""
    return HERE / design.results_folder(name).name


def main() -> None:
    """Run the pending sessions given on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--workspaces", type=Path, required=True,
                        help="folder with the M and E workspaces (study/cain2027/build_workspaces.py)")
    parser.add_argument("--scratch", type=Path, required=True, help="where session copies go (outside the repository)")
    parser.add_argument("--model", required=True, help="the Codex model for every session")
    parser.add_argument("--cases", default="", help="comma-separated case ids (default: all)")
    parser.add_argument("--cases-dir", type=Path, default=CASES, help="the cases folder (default: cases/)")
    parser.add_argument("--conditions", default="M,E,N")
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--skills-via", choices=SKILLS_VIA, default="files",
                        help="files: .agents/skills/<name>/SKILL.md in the work copy; prompt: append it to the prompt")
    parser.add_argument("--keep-raw", action="store_true", help="keep raw logs and session copies (debugging)")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="seconds per session before it fails")
    parser.add_argument("--oss", metavar="PROVIDER", help="run the model through a local provider (e.g. ollama)")
    parser.add_argument("--results", default="results", help="results folder: results (default) or results-<label>")
    args = parser.parse_args()
    try:
        results = results_folder(args.results)
    except ValueError as exc:
        sys.exit(str(exc))
    refused = guards(results, model=args.model, prompt=PROMPT, skills_via=args.skills_via)
    if refused:
        sys.exit("\n".join(refused))
    repo = HERE.parents[1]
    if cain.inside(args.scratch, repo) or cain.inside(args.workspaces, repo):
        sys.exit("Run sessions outside the repository (--scratch and --workspaces), so agents cannot read it.")
    conditions = args.conditions.split(",")
    unknown = [c for c in conditions if c not in CONDITIONS]
    if unknown:
        sys.exit(f"Unknown condition(s) {', '.join(unknown)}: use {', '.join(CONDITIONS)}.")
    try:
        cases = load_cases(args.cases_dir)
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
    wanted = set(filter(None, args.cases.split(",")))
    cases = [c for c in cases if not wanted or c["id"] in wanted]
    if not cases:
        sys.exit(f"No cases in {args.cases_dir}{' matching --cases' if wanted else ''} (see cases/README.md).")
    ddspace_bin = Path(sys.executable).with_name("ddspace")
    ddspace_bin = ddspace_bin if ddspace_bin.is_file() else (Path(shutil.which("ddspace")) if shutil.which("ddspace")
                                                             else None)
    if ddspace_bin is None:
        sys.exit("No ddspace command next to this Python or on the PATH: every condition needs it.")
    key = os.environ.get("STUDY_OPENAI_API_KEY")
    if not key and set(conditions) & set(SPACE_CONDITIONS):
        print("warning: STUDY_OPENAI_API_KEY is not set; ddspace point descriptions will fail "  # noqa: T201
              "(the skills then fall back to --no-llm)")
    version = cain.codex_version()
    print(f"{version or 'codex version unknown'}; model {args.model}"  # noqa: T201
          f"{f' via {args.oss}' if args.oss else ''}; skills via {args.skills_via}; results in {results.name}/")
    for s in pending(plan(cases, conditions, args.reps), results):
        case = next(c for c in cases if c["id"] == s.case)
        try:
            rec = run(s, case, args.workspaces.resolve(), args.scratch.resolve(), model=args.model, results=results,
                      skills_via=args.skills_via, keep_raw=args.keep_raw, ddspace_bin=ddspace_bin,
                      timeout=args.timeout, oss=args.oss, version=version, key=key)
        except Exception as exc:                          # one broken session must not stop the batch
            print(f"{s.id}: error {type(exc).__name__}: {exc}")  # noqa: T201
            continue
        check = rec.get("check") or {}
        print(f"{s.id}: {rec['status']}; check {'ok' if check.get('ok') else 'not clean'}, "  # noqa: T201
              f"{rec.get('check_runs', 0)} check runs {'; '.join(rec['problems'])}")


if __name__ == "__main__":
    main()
