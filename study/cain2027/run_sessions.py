#!/usr/bin/env python3
r"""Run the study sessions: one ``codex exec`` per brief, condition and repetition, each in a fresh copy.

For each session the runner copies the condition's workspace (empty for N) into a scratch folder with the
brief as ``BRIEF.md``, gives Codex a private home holding only its login (no user skills, memories or
config), checks the controls before and after the run, and keeps two files:

- ``results/designs/<id>.json``: the design (schema-valid, keys and the home folder redacted);
- ``results/summaries/<id>.json``: an allow-listed summary of the event log (ddspace calls, point events,
  tokens, time, flags); raw logs and scratch copies are deleted unless ``--keep-raw``.

Only M and E sessions get sandbox network access and the study key (for ``ddspace point`` descriptions); the
summary flags any other network use, and web search is disabled in every session.

Usage::

    STUDY_OPENAI_API_KEY=... python study/cain2027/run_sessions.py --workspaces <folder> --scratch <folder> \\
        --model <codex model> [--briefs fraud,vision] [--conditions N,M,E] [--reps 2]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MANIFEST = HERE / "inputs" / "manifest.json"
MANIFEST_COPY = design.MANIFEST_COPY
MATCHING_MODEL = design.matching_model()   # the matcher's judge (KTD10); the session model must differ
CONDITIONS = ("N",) + design.SPACE_CONDITIONS
TIMEOUT = 1800                             # seconds per session before it is stopped and failed
# The only variables a session inherits (plus PATH, CODEX_HOME and, for M and E, the study key).
SAFE_ENV = ("HOME", "USER", "LOGNAME", "SHELL", "TERM", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE")
SPACE_CONDITIONS = design.SPACE_CONDITIONS
WEB_SEARCH_OFF = 'web_search="disabled"'
NETWORK_ON = "sandbox_workspace_write.network_access=true"
# Tool surfaces the study does not want (the agent works with the shell and the workspace only).
DISABLED_FEATURES = ("browser_use", "browser_use_external", "in_app_browser", "computer_use", "apps", "plugins",
                     "memories")
_NETWORK = re.compile(r"(^|[\s;&|(])(curl|wget|pip3?|npm|npx|uv|conda|brew|git\s+clone|nc|ssh)\b"
                      r"|import\s+(requests|urllib|httpx|openai)|https?://")
_SEGMENTS = re.compile(r"&&|\|\||;|\n|\|")
_SHELL = re.compile(r"^\S*(?:sh|bash|zsh)\s+-l?c\s+(.*)$", re.S)


@dataclass(frozen=True)
class Session:
    """One agent session: a brief, a condition (N, M or E) and a repetition number."""

    brief: str
    condition: str
    rep: int

    @property
    def id(self) -> str:
        """Return the session id, e.g. ``fraud-M-r1``."""
        return f"{self.brief}-{self.condition}-r{self.rep}"


def plan(briefs: List[Dict[str, Any]], conditions: Iterable[str], reps: int) -> List[Session]:
    """All sessions, brief by brief (so a partial run still covers every condition of the first briefs)."""
    return [Session(b["id"], c, r) for b in briefs for r in range(1, reps + 1) for c in conditions]


def pending(sessions: List[Session], results: Path = RESULTS) -> List[Session]:
    """Return the sessions that have no design yet."""
    return [s for s in sessions if not (results / "designs" / f"{s.id}.json").is_file()]


def command(session: Session, workdir: Path, last: Path, *, model: str) -> List[str]:
    """Return the ``codex exec`` argv for one session."""
    argv = ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config",
            "-s", "workspace-write", "-m", model, "--output-schema", str(design.SCHEMA), "-o", str(last),
            "-C", str(workdir), "-c", WEB_SEARCH_OFF]
    for feature in DISABLED_FEATURES:
        argv += ["--disable", feature]
    if session.condition in SPACE_CONDITIONS:
        argv += ["-c", NETWORK_ON, "-c", "shell_environment_policy.ignore_default_excludes=true"]
    return argv + ["-"]   # the prompt comes on stdin


def preflight(session: Session, argv: List[str], workdir: Path, manifest: Path = MANIFEST, *,
              model: str, matching_model: str = MATCHING_MODEL) -> List[str]:
    """Return why the session must not start (empty when every control holds)."""
    problems = []
    if not model or argv[argv.index("-m") + 1] != model:
        problems.append("the session model is not pinned")
    if model.split("/")[-1] == matching_model.split("/")[-1]:
        problems.append(f"the session model equals the matching model {matching_model}")
    if WEB_SEARCH_OFF not in argv:
        problems.append("web search is not disabled")
    if (NETWORK_ON in argv) != (session.condition in SPACE_CONDITIONS):
        problems.append("network access does not match the condition")
    if session.condition in SPACE_CONDITIONS:
        copy = workdir / MANIFEST_COPY
        if not copy.is_file() or json.loads(copy.read_text()) != json.loads(manifest.read_text()):
            problems.append("the workspace manifest does not match the study inputs")
    return problems


def _inner(command_line: str) -> str:
    """Return the script a shell wrapper (``/bin/zsh -lc '...'``) runs."""
    m = _SHELL.match(command_line.strip())
    if not m:
        return command_line
    try:
        parts = shlex.split(m.group(1))
        return parts[0] if len(parts) == 1 else m.group(1)
    except ValueError:
        return m.group(1)


def _ddspace_calls(script: str) -> List[List[str]]:
    """Return the argument lists of every ddspace invocation in a shell script."""
    calls = []
    for piece in _SEGMENTS.split(script):
        args = _ddspace_args(piece)
        if args is not None:
            calls.append(args)
    return calls


def _ddspace_args(piece: str) -> Optional[List[str]]:
    """Return the arguments when one shell segment invokes ddspace, else None."""
    try:
        words = shlex.split(piece)
    except ValueError:
        return None
    for i, w in enumerate(words):
        if Path(w).name == "ddspace" or w.endswith("delvedspace.cli"):
            return words[i + 1:]
    return None


def _uses_network(script: str) -> bool:
    """Whether any shell segment other than a ddspace call reaches the network (curl, pip, a URL, ...)."""
    return any(_NETWORK.search(piece) and _ddspace_args(piece) is None for piece in _SEGMENTS.split(script))


def _point_event(args: List[str], output: str, ok: bool, clean) -> Dict[str, Any]:
    values, skip = [], False
    for a in args[1:]:
        if skip:
            skip = False
        elif a in ("--graph", "--model"):
            skip = True
        elif not a.startswith("--"):
            values.append(clean(a))
    warnings = attested = 0
    try:
        data = json.loads(output[output.index("{"):]) if "{" in output else {}
        warnings, attested = len(data.get("warnings") or []), len(data.get("attested_by") or [])
    except ValueError:
        pass
    return {"values": values, "ok": ok, "warnings": warnings, "attested": attested, "llm": "--no-llm" not in args}


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
        script = _inner(str(item.get("command") or ""))
        ddspace = _ddspace_calls(script)
        for args in ddspace:
            if not args:
                continue
            name = " ".join(args[:2]) if args[0] in ("query", "wiki", "agent") and len(args) > 1 else args[0]
            calls[name] += 1
            if args[0] == "point":
                points.append(_point_event(args, str(item.get("aggregated_output") or ""),
                                           item.get("exit_code") == 0, clean))
        if _uses_network(script):
            network += 1
    return {"complete": complete, "commands": commands, "ddspace_calls": dict(calls), "points": points,
            "network_commands": network, "web_search": web, "tokens": tokens}


def postflight(summary: Dict[str, Any], last: Path) -> List[str]:
    """Return why a finished session does not count (empty when it does)."""
    problems = []
    if not summary["complete"]:
        problems.append("the event log is not complete (no turn.completed)")
    if summary["web_search"]:
        problems.append("the agent used web search")
    if not last.is_file() or not last.read_text(encoding="utf-8").strip():
        problems.insert(0, "no design: Codex wrote no last message")
        return problems
    try:
        problems += design.validate(json.loads(last.read_text(encoding="utf-8")))
    except ValueError as exc:
        problems.append(f"the design is not JSON: {exc}")
    return problems


def _codex_home(root: Path) -> Path:
    """Create a private CODEX_HOME holding only the login of the user's Codex."""
    home = root / "codex-home"
    home.mkdir(parents=True, exist_ok=True)
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    if auth.is_file():
        shutil.copyfile(auth, home / "auth.json")
        (home / "auth.json").chmod(0o600)
    return home


def _environment(session: Session, codex_home: Path, ddspace_bin: Optional[Path], key: Optional[str]) -> Dict[str, str]:
    """Return the session's environment: an allow-list, never the operator's secrets."""
    path = [p for p in os.environ.get("PATH", "").split(os.pathsep)
            if not (Path(p) / "ddspace").exists()]                  # N: no ddspace on the PATH
    env = {k: os.environ[k] for k in SAFE_ENV if k in os.environ}
    env.update(CODEX_HOME=str(codex_home), PATH=os.pathsep.join(path))
    if session.condition in SPACE_CONDITIONS:
        if ddspace_bin is not None:
            env["PATH"] = os.pathsep.join([str(ddspace_bin.parent), env["PATH"]])
        if key:
            env["OPENAI_API_KEY"] = key
    return env


def _events(stdout: str) -> List[Dict[str, Any]]:
    """Parse the JSONL event stream, skipping lines that are not JSON objects."""
    events = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def run(session: Session, brief: Dict[str, Any], workspaces: Path, scratch: Path, *, model: str,
        results: Path = RESULTS, keep_raw: bool = False, ddspace_bin: Optional[Path] = None,
        key: Optional[str] = None, timeout: int = TIMEOUT) -> Dict[str, Any]:
    """Run one session; write its design and summary; return the summary."""
    root = scratch / session.id
    shutil.rmtree(root, ignore_errors=True)
    try:
        return _run(session, brief, workspaces, root, model=model, results=results, keep_raw=keep_raw,
                    ddspace_bin=ddspace_bin, key=key, timeout=timeout)
    finally:
        shutil.rmtree(root / "codex-home", ignore_errors=True)     # the copied login never outlives the session
        if not keep_raw:
            shutil.rmtree(root, ignore_errors=True)


def _run(session: Session, brief: Dict[str, Any], workspaces: Path, root: Path, *, model: str, results: Path,
         keep_raw: bool, ddspace_bin: Optional[Path], key: Optional[str], timeout: int) -> Dict[str, Any]:
    workdir = root / "ws"
    if session.condition in SPACE_CONDITIONS:
        shutil.copytree(workspaces / session.condition, workdir)
    else:
        workdir.mkdir(parents=True)
    (workdir / "BRIEF.md").write_text(f"# {brief['system']}\n\n{brief['text'].strip()}\n", encoding="utf-8")
    last = root / "last.json"
    argv = command(session, workdir, last, model=model)
    argv[0] = shutil.which("codex") or "codex"           # resolved here: the session PATH may not have it
    record = {"session": session.id, "brief": session.brief, "condition": session.condition, "rep": session.rep,
              "model": model, "matching_model": MATCHING_MODEL,
              "prompt_sha256": design.sha256(design.PROMPT), "schema_sha256": design.sha256(design.SCHEMA),
              "started_at": datetime.now().isoformat(timespec="seconds")}
    problems = preflight(session, argv, workdir, model=model)
    summary: Dict[str, Any] = {}
    if not problems:
        env = _environment(session, _codex_home(root), ddspace_bin, key)
        start = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(argv, input=design.PROMPT.read_text(encoding="utf-8"), capture_output=True,
                                  text=True, env=env, timeout=timeout)
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
        summary = summarize(_events(stdout), home=str(Path.home()), secrets=[key] if key else [])
        problems = ([f"timed out after {timeout} s"] if timed_out else []) + postflight(summary, last)
    record.update(summary, status="failed" if problems else "ok", problems=problems)
    (results / "summaries").mkdir(parents=True, exist_ok=True)
    (results / "summaries" / f"{session.id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if not problems:
        text = design.redact(last.read_text(encoding="utf-8"), str(Path.home()), [key] if key else [])
        (results / "designs").mkdir(parents=True, exist_ok=True)
        (results / "designs" / f"{session.id}.json").write_text(
            json.dumps(json.loads(text), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def inside(path: Path, folder: Path) -> bool:
    """Whether ``path`` is ``folder`` or lies below it."""
    resolved, folder = path.resolve(), folder.resolve()
    return resolved == folder or folder in resolved.parents


def main() -> None:
    """Run the pending sessions given on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--workspaces", type=Path, required=True, help="folder with N, M and E (build_workspaces.py)")
    parser.add_argument("--scratch", type=Path, required=True, help="where session copies go (outside the repository)")
    parser.add_argument("--model", required=True, help="the Codex model for every session")
    parser.add_argument("--briefs", default="", help="comma-separated brief ids (default: all)")
    parser.add_argument("--conditions", default="N,M,E")
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--keep-raw", action="store_true", help="keep raw logs and session copies (debugging)")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="seconds per session before it fails")
    args = parser.parse_args()
    repo = HERE.parents[1]
    if inside(args.scratch, repo) or inside(args.workspaces, repo):
        sys.exit("Run sessions outside the repository (--scratch and --workspaces), so agents cannot read it.")
    conditions = args.conditions.split(",")
    unknown = [c for c in conditions if c not in CONDITIONS]
    if unknown:
        sys.exit(f"Unknown condition(s) {', '.join(unknown)}: use {', '.join(CONDITIONS)}.")
    briefs = design.load_briefs()
    wanted = set(filter(None, args.briefs.split(",")))
    briefs = [b for b in briefs if not wanted or b["id"] in wanted]
    key = os.environ.get("STUDY_OPENAI_API_KEY")
    if not key and set(conditions) & set(SPACE_CONDITIONS):
        print("warning: STUDY_OPENAI_API_KEY is not set; ddspace point descriptions will fail (use --no-llm)")  # noqa: T201
    ddspace_bin = Path(sys.executable).with_name("ddspace")
    for s in pending(plan(briefs, conditions, args.reps)):
        brief = next(b for b in briefs if b["id"] == s.brief)
        try:
            rec = run(s, brief, args.workspaces.resolve(), args.scratch.resolve(), model=args.model,
                      keep_raw=args.keep_raw, ddspace_bin=ddspace_bin if ddspace_bin.is_file() else None, key=key,
                      timeout=args.timeout)
        except Exception as exc:                          # one broken session must not stop the batch
            print(f"{s.id}: error {type(exc).__name__}: {exc}")  # noqa: T201
            continue
        print(f"{s.id}: {rec['status']} {'; '.join(rec['problems'])}")  # noqa: T201


if __name__ == "__main__":
    main()
