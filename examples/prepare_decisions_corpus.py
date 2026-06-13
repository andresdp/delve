"""Prepare a flat corpus from architecture design decisions JSON.

Reads examples/decisions_results.json and outputs examples/architecture_decisions.json
as a flat array of strings combining description, pattern, and rationale.

Usage:
    python examples/prepare_decisions_corpus.py
"""

import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "decisions_results.json"
OUTPUT_FILE = Path(__file__).parent / "architecture_decisions.json"


def main() -> None:
    with open(INPUT_FILE) as f:
        data = json.load(f)

    decisions = data["design_decisions"]
    corpus = []

    for dd in decisions:
        description = dd.get("description", "").strip()
        pattern = dd.get("pattern", "").strip()
        rationale = dd.get("rationale", "").strip()

        # Combine: description (Pattern). Rationale.
        parts = []
        if description:
            parts.append(description)
        if pattern:
            parts.append(f"({pattern})")
        if rationale:
            parts.append(rationale)

        text = " ".join(parts)
        if text:
            corpus.append(text)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(corpus)} documents → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()