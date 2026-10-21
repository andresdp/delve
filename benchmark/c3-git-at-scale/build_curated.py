#!/usr/bin/env python3
"""Build the id-bearing C3-curated corpus from the 16 curated write-ups only.

``examples/cursor-git-at-scale/build_corpus.py`` globs every ``.md`` file in its
folder, which also holds earlier Delve run reports (``*_report_*.md``). This
wrapper reuses its frontmatter handling but reads only the six numbered lens
folders (``01-context/`` .. ``06-evolution/``), so no Delve output can enter the
corpus. Writes ``examples/c3-git-at-scale/c3-git-at-scale-curated_documents.json``
as ``{"id", "title", "content"}`` objects (id = file slug).

Usage::

    python benchmark/c3-git-at-scale/build_curated.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CURATED = REPO / "examples" / "cursor-git-at-scale"
OUT = REPO / "examples" / "c3-git-at-scale" / "c3-git-at-scale-curated_documents.json"
EXPECTED = 16


def _strip_frontmatter():
    spec = importlib.util.spec_from_file_location("curated_builder", CURATED / "build_corpus.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.strip_frontmatter


def main() -> int:
    strip_frontmatter = _strip_frontmatter()
    files = sorted(CURATED.glob("0[1-6]-*/*.md"))
    if len(files) != EXPECTED:
        print(f"expected {EXPECTED} curated documents, found {len(files)}", file=sys.stderr)
        return 1
    entries = []
    for p in files:
        title, body = strip_frontmatter(p.read_text(encoding="utf-8"))
        content = f"# {title}\n\n{body}" if title else body
        entries.append({"id": p.stem, "title": title or p.stem, "content": content})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(entries)} curated documents to {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
