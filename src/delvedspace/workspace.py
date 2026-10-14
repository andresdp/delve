"""A DelveDSpace workspace: the folder layout, ``ddspace.yaml`` and its few machine-written values."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

CONFIG_NAME = "ddspace.yaml"
STATE_DIR = ".ddspace"
SOURCE_SUFFIXES = {".md": "md", ".markdown": "md", ".txt": "txt", ".html": "html", ".htm": "html", ".pdf": "pdf"}

# API key per LLM provider prefix ("openai/gpt-..."); ollama runs locally without one.
PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "ollama": None,
}

GITIGNORE = """\
# DelveDSpace workspace. Source text is third-party content: keep it out of version control.
sources/
corpus.json
.env
.ddspace/
# Run outputs that embed source text (the taxonomy JSON, report and design points are safe to commit).
runs/*/*_documents_*.json
runs/*/*_clusters_*.json
runs/*/*_open_codes_*.json
runs/*/*_messages_*.json
runs/*/*_html_report_*.html
runs/*/corpus*.json
"""


class WorkspaceError(Exception):
    """A workspace is missing or inconsistent; the message says what to do."""


@dataclass
class Settings:
    """The answers ``ddspace init`` writes into a new ``ddspace.yaml``."""

    name: str
    use_case: str
    generation_llm: str = "openai/gpt-5.6-luna"
    evaluation_llm: str = "openai/gpt-5.6-luna"
    embedding: str = "openai/text-embedding-3-small"
    sources_dir: str = "sources"
    max_dimensions: Optional[int] = None
    batch_size: int = 10
    critic: bool = True


def _scalar(value: Any) -> str:
    """Render a value as a one-line YAML scalar (strings double-quoted)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def render_config(settings: Settings) -> str:
    """Return the text of a new ``ddspace.yaml`` with the given answers, keeping every comment."""
    text = resources.files("delvedspace").joinpath("templates/ddspace.yaml").read_text(encoding="utf-8")
    values = {
        "GENERATION_LLM": settings.generation_llm, "EVALUATION_LLM": settings.evaluation_llm,
        "EMBEDDING": settings.embedding, "BATCH_SIZE": settings.batch_size, "NAME": settings.name,
        "MAX_DIMENSIONS": settings.max_dimensions, "USE_CASE": " ".join(settings.use_case.split()),
        "CRITIC": settings.critic, "SOURCES_DIR": settings.sources_dir,
    }
    return re.sub(r"__([A-Z_]+)__", lambda m: _scalar(values[m.group(1)]), text)


def set_value(text: str, dotted: str, value: Any) -> str:
    """Replace the value of ``block.key`` in YAML text, keeping comments and layout.

    Only two-level keys under a top-level block are supported (``workspace.current_run``,
    ``wiki.quotes``); the key must already be in the file.
    """
    block, key = dotted.split(".")
    lines = text.splitlines(keepends=True)
    in_block = False
    for i, line in enumerate(lines):
        if re.match(r"^\S", line):
            in_block = line.startswith(f"{block}:")
            continue
        m = re.match(rf"^(\s+{re.escape(key)}:)[^\n]*(\n?)$", line)
        if in_block and m:
            lines[i] = f"{m.group(1)} {_scalar(value)}{m.group(2)}"
            return "".join(lines)
    raise WorkspaceError(f"{CONFIG_NAME} has no `{dotted}` setting; add it under `{block}:`")


class Workspace:
    """Paths and settings of one workspace folder."""

    def __init__(self, root: Path):
        """Use ``root`` (the folder holding ``ddspace.yaml``)."""
        self.root = Path(root).resolve()

    @classmethod
    def find(cls, start: Optional[Path] = None) -> Workspace:
        """Return the workspace containing ``start`` (default: the current folder)."""
        here = Path(start or os.getcwd()).resolve()
        for folder in (here, *here.parents):
            if (folder / CONFIG_NAME).is_file():
                return cls(folder)
        raise WorkspaceError(f"No {CONFIG_NAME} here or in a parent folder. Run `ddspace init` first.")

    # ---------------------------------------------------------------- paths

    @property
    def config_path(self) -> Path:
        """The workspace settings file."""
        return self.root / CONFIG_NAME

    @property
    def state_dir(self) -> Path:
        """Machine-managed state (gitignored)."""
        return self.root / STATE_DIR

    @property
    def text_dir(self) -> Path:
        """Extracted plain text per source (``sNN.md``)."""
        return self.state_dir / "text"

    @property
    def manifest_path(self) -> Path:
        """Extraction record per source (file, hash, words, flags)."""
        return self.state_dir / "sources.json"

    @property
    def sources_dir(self) -> Path:
        """The folder with the user's source files."""
        return self.root / str(self.config().get("workspace", {}).get("sources_dir") or "sources")

    @property
    def sources_csv(self) -> Path:
        """Metadata per source (id, file, title, url, type)."""
        return self.root / "sources.csv"

    @property
    def corpus_path(self) -> Path:
        """The passages Delve mines."""
        return self.root / "corpus.json"

    @property
    def runs_dir(self) -> Path:
        """One folder per pipeline run."""
        return self.root / "runs"

    @property
    def env_path(self) -> Path:
        """API keys (gitignored)."""
        return self.root / ".env"

    # ---------------------------------------------------------------- settings

    def config(self) -> Dict[str, Any]:
        """Return ``ddspace.yaml`` as a dict."""
        try:
            return yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise WorkspaceError(f"{CONFIG_NAME} is not valid YAML: {exc}") from exc

    def set(self, dotted: str, value: Any) -> None:
        """Write one machine-managed value (e.g. ``workspace.current_run``) into ``ddspace.yaml``."""
        self.config_path.write_text(set_value(self.config_path.read_text(encoding="utf-8"), dotted, value),
                                    encoding="utf-8")

    def env_value(self, name: str) -> Optional[str]:
        """Return an environment variable, or its value in the workspace ``.env`` file."""
        if os.environ.get(name):
            return os.environ[name]
        if self.env_path.is_file():
            for line in self.env_path.read_text(encoding="utf-8").splitlines():
                key, sep, value = line.partition("=")
                if sep and key.strip() == name and value.strip():
                    return value.strip().strip("'\"")
        return None

    def write_env(self, name: str, value: str) -> None:
        """Add or replace ``name=value`` in the workspace ``.env`` (readable by the owner only)."""
        lines = self.env_path.read_text(encoding="utf-8").splitlines() if self.env_path.is_file() else []
        lines = [line for line in lines if line.partition("=")[0].strip() != name] + [f"{name}={value}"]
        self.env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.env_path.chmod(0o600)


def provider_key(model: str) -> Optional[str]:
    """Return the API-key variable a ``provider/model`` string needs (None for local providers)."""
    provider = model.split("/", 1)[0].lower() if "/" in model else "openai"
    return PROVIDER_KEYS.get(provider, f"{provider.upper()}_API_KEY")


def create(root: Path, settings: Settings) -> Workspace:
    """Create the layout, ``ddspace.yaml`` and ``.gitignore`` in ``root``."""
    ws = Workspace(root)
    ws.root.mkdir(parents=True, exist_ok=True)
    ws.config_path.write_text(render_config(settings), encoding="utf-8")
    (ws.root / settings.sources_dir).mkdir(parents=True, exist_ok=True)
    ws.runs_dir.mkdir(exist_ok=True)
    gitignore = ws.root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(GITIGNORE.replace("sources/", f"{settings.sources_dir.rstrip('/')}/", 1),
                             encoding="utf-8")
    return ws


def source_files(folder: Path) -> list[Path]:
    """Return the supported source files under ``folder`` (recursive; hidden files skipped), sorted."""
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.rglob("*")
                  if p.is_file() and p.suffix.lower() in SOURCE_SUFFIXES
                  and not any(part.startswith(".") for part in p.relative_to(folder).parts))
