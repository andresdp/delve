"""Session controls and event parsing for the Designing 2027 runner.

These helpers were first imported from an earlier study's runner; they are copied here, unchanged in behaviour,
so this folder runs on its own: the Codex flags the study pins (web search off, network on, tool surfaces off),
the environment allow-list, the parsing of Codex's JSONL events and shell commands, and the redaction of keys
and the home folder.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

TIMEOUT = 1800                             # seconds per session before it is stopped and failed
# The only variables a session inherits (plus PATH, CODEX_HOME and the study key).
SAFE_ENV = ("HOME", "USER", "LOGNAME", "SHELL", "TERM", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE")
WEB_SEARCH_OFF = 'web_search="disabled"'
NETWORK_ON = "sandbox_workspace_write.network_access=true"
# Tool surfaces the study does not want (the agent works with the shell and the workspace only).
DISABLED_FEATURES = ("browser_use", "browser_use_external", "in_app_browser", "computer_use", "apps", "plugins",
                     "memories")
MANIFEST_COPY = "study-manifest.json"      # the input manifest, as copied into each workspace with a space

_NETWORK = re.compile(r"(^|[\s;&|(])(curl|wget|pip3?|npm|npx|uv|conda|brew|git\s+clone|nc|ssh)\b"
                      r"|import\s+(requests|urllib|httpx|openai)|https?://")
_SEGMENTS = re.compile(r"&&|\|\||;|\n|\|")
_SHELL = re.compile(r"^\S*(?:sh|bash|zsh)\s+-l?c\s+(.*)$", re.S)
_KEY = re.compile(r"sk-[A-Za-z0-9_\-]{12,}")
_RESULTS_NAME = re.compile(r"^results(-[A-Za-z0-9._-]+)?$")


def sha256(path: Path) -> str:
    """Hex SHA-256 of a file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def check_results_name(name: str) -> str:
    """``name`` when it is ``results`` or ``results-<label>`` (so the raw-log ignore rule ``results*/raw/`` covers
    it); raise otherwise."""
    if not _RESULTS_NAME.match(name):
        raise ValueError(f"results folder {name!r}: use 'results' or 'results-<label>' (letters, digits, . _ -)")
    return name


def native_prefix() -> List[str]:
    """``/usr/bin/arch -arm64`` when this Python runs translated by Rosetta, else nothing.

    A translated (x86_64) Python starts Node as x86_64 too, and Codex then looks for its x64 build.
    """
    if sys.platform != "darwin":
        return []
    try:
        translated = subprocess.run(["/usr/sbin/sysctl", "-n", "sysctl.proc_translated"], capture_output=True,
                                    text=True).stdout.strip()
    except OSError:
        return []
    return ["/usr/bin/arch", "-arm64"] if translated == "1" else []


NATIVE = native_prefix()


def codex_version() -> Optional[str]:
    """The installed Codex CLI version (``codex-cli X.Y.Z``), recorded in every summary."""
    try:
        out = subprocess.run(NATIVE + [shutil.which("codex") or "codex", "--version"], capture_output=True,
                             text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out or None


def codex_home(root: Path) -> Path:
    """Create a private CODEX_HOME holding only the login of the user's Codex."""
    home = root / "codex-home"
    home.mkdir(parents=True, exist_ok=True)
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    if auth.is_file():
        shutil.copyfile(auth, home / "auth.json")
        (home / "auth.json").chmod(0o600)
    return home


def manifest_problems(workdir: Path, manifest: Path) -> List[str]:
    """Why the workspace in ``workdir`` does not come from the inputs ``manifest`` lists (empty when it does).

    Every file the manifest lists must appear, with the same SHA-256, in the workspace's copy of the manifest.
    """
    copy = workdir / MANIFEST_COPY
    try:
        theirs = (json.loads(copy.read_text(encoding="utf-8")).get("files") or {})
        ours = (json.loads(Path(manifest).read_text(encoding="utf-8")).get("files") or {})
    except (OSError, ValueError):
        return ["the workspace manifest does not match the study inputs"]
    if not ours or any(theirs.get(name) != digest for name, digest in ours.items()):
        return ["the workspace manifest does not match the study inputs"]
    return []


def inner(command_line: str) -> str:
    """Return the script a shell wrapper (``/bin/zsh -lc '...'``) runs."""
    m = _SHELL.match(command_line.strip())
    if not m:
        return command_line
    try:
        parts = shlex.split(m.group(1))
        return parts[0] if len(parts) == 1 else m.group(1)
    except ValueError:
        return m.group(1)


def ddspace_args(piece: str) -> Optional[List[str]]:
    """Return the arguments when one shell segment invokes ddspace, else None."""
    try:
        words = shlex.split(piece)
    except ValueError:
        return None
    for i, w in enumerate(words):
        if Path(w).name == "ddspace" or w.endswith("delvedspace.cli"):
            return words[i + 1:]
    return None


def ddspace_calls_naive(script: str) -> List[List[str]]:
    """The argument lists of every ddspace invocation, splitting at every ``;`` ``&`` ``|`` and newline.

    It also splits inside quotes; the runner's own splitter does not, and is used to count design points. This
    one is kept for the counts that the recorded summaries were made with (``ddspace_calls``).
    """
    calls = []
    for piece in _SEGMENTS.split(script):
        args = ddspace_args(piece)
        if args is not None:
            calls.append(args)
    return calls


def uses_network(script: str) -> bool:
    """Whether any shell segment other than a ddspace call reaches the network (curl, pip, a URL, ...)."""
    return any(_NETWORK.search(piece) and ddspace_args(piece) is None for piece in _SEGMENTS.split(script))


def point_event(args: List[str], output: str, ok: bool, clean) -> Dict[str, Any]:
    """Summarize one ``ddspace point`` call: its values (cleaned), whether it succeeded, warnings, attestations."""
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


def events(stdout: str) -> List[Dict[str, Any]]:
    """Parse the JSONL event stream, skipping lines that are not JSON objects."""
    out = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            out.append(event)
    return out


def inside(path: Path, folder: Path) -> bool:
    """Whether ``path`` is ``folder`` or lies below it."""
    resolved, folder = Path(path).resolve(), Path(folder).resolve()
    return resolved == folder or folder in resolved.parents
