"""Split source texts into passages of roughly equal size (the corpus ddspace mines).

Moved from ``benchmark/build_corpus.py``, which imports it back. Passages break at
paragraph and heading boundaries, never inside a fenced code block. Passage ids have the
form ``s03_p02`` (source 3, passage 2), so every open code and value keeps its provenance.
"""

from __future__ import annotations

import re
from typing import List, Tuple

TARGET_WORDS, MIN_WORDS, MAX_WORDS = 300, 80, 450

IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]+)\]\((?:[^()\s]|\([^)]*\))*\)")
AUTOLINK = re.compile(r"<https?://[^>]+>")
BARE_URL = re.compile(r"https?://\S+")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])")
LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}
LIST_ITEM = re.compile(r"^\s*([-*•●▪]|\d+[.)])\s+")


def words(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split())


def reflow(text: str) -> str:
    """Join hard-wrapped lines inside paragraphs (PDF/slide text); keep list items."""
    out = []
    for block in text.split("\n\n"):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        merged: List[str] = []
        for line in lines:
            if merged and not LIST_ITEM.match(line):
                merged[-1] = merged[-1] + " " + line
            else:
                merged.append(line)
        out.append("\n".join(merged))
    return "\n\n".join(out)


def clean(text: str, from_pdf: bool = False) -> str:
    """Remove markdown noise that carries no meaning for coding."""
    for lig, repl in LIGATURES.items():
        text = text.replace(lig, repl)
    text = IMAGE.sub("", text)
    text = LINK.sub(r"\1", text)
    text = AUTOLINK.sub("", text)
    text = BARE_URL.sub("", text)
    text = text.replace("**", "").replace("__", "")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"[-*•●▪]\s*", stripped):    # empty bullet
            continue
        if re.fullmatch(r"\d{1,4}", stripped):         # stray vote/karma/page numbers
            continue
        lines.append(line.rstrip())
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return reflow(text) if from_pdf else text


def blocks(text: str) -> List[str]:
    """Split into paragraph blocks; a fenced code block is always one block."""
    out, buf, in_code = [], [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            buf.append(line)
            if not in_code:          # closing fence ends the block
                out.append("\n".join(buf))
                buf = []
            continue
        if in_code:
            buf.append(line)
        elif line.strip():
            buf.append(line)
        elif buf:
            out.append("\n".join(buf))
            buf = []
    if buf:
        out.append("\n".join(buf))
    return [b.strip() for b in out if b.strip()]


def _pack(units: List[str], target: int, sep: str) -> List[str]:
    parts, cur = [], []
    for u in units:
        if cur and words(sep.join(cur + [u])) > target:
            parts.append(sep.join(cur))
            cur = []
        cur.append(u)
    if cur:
        parts.append(sep.join(cur))
    return parts


def split_long(block: str, target: int) -> List[str]:
    """Split an oversized block: by lines first (lists, tables), then by sentences.

    Fenced code blocks stay whole.
    """
    if block.lstrip().startswith("```"):
        return [block]
    lines = [line for line in block.splitlines() if line.strip()]
    if len(lines) > 1:
        out = []
        for part in _pack(lines, target, "\n"):
            out.extend(split_long(part, target) if words(part) > target * 1.5 and "\n" not in part else [part])
        return out
    return _pack(SENTENCE_END.split(block), target, " ")


def segment(text: str, target: int = TARGET_WORDS, min_words: int = MIN_WORDS,
            max_words: int = MAX_WORDS) -> List[Tuple[str, str]]:
    """Group blocks into passages of ~target words. Returns (section, passage) pairs."""
    passages: List[Tuple[str, str]] = []
    section, chunk_section, chunk = "", "", []

    def flush():
        nonlocal chunk
        if chunk:
            passages.append((chunk_section, "\n\n".join(chunk)))
            chunk = []

    for block in blocks(text):
        m = HEADING.match(block) if "\n" not in block else None
        if m:
            # Prefer breaking at a heading once the chunk has enough material
            # (half the target), so many short sections do not each become a
            # tiny passage.
            if words("\n\n".join(chunk)) >= max(min_words, target // 2):
                flush()
            section = m.group(2).strip().strip("#").strip()
        pieces = split_long(block, target) if words(block) > max_words else [block]
        for piece in pieces:
            if not chunk:
                chunk_section = section
            if chunk and words("\n\n".join(chunk + [piece])) > max_words:
                flush()
                chunk_section = section
            chunk.append(piece)
            if words("\n\n".join(chunk)) >= target:
                flush()
    flush()
    return merge_short(passages, min_words)


def merge_short(passages: List[Tuple[str, str]], min_words: int) -> List[Tuple[str, str]]:
    """Merge every passage under ``min_words`` into its smaller neighbour."""
    out = list(passages)
    i = 0
    while len(out) > 1 and i < len(out):
        if words(out[i][1]) >= min_words:
            i += 1
            continue
        prev_w = words(out[i - 1][1]) if i > 0 else None
        next_w = words(out[i + 1][1]) if i + 1 < len(out) else None
        if next_w is None or (prev_w is not None and prev_w <= next_w):
            sec, text = out[i - 1]
            out[i - 1] = (sec, text + "\n\n" + out[i][1])
            del out[i]
            i = max(i - 1, 0)
        else:
            sec, text = out[i]
            out[i] = (sec, text + "\n\n" + out[i + 1][1])
            del out[i + 1]
    return out


def source_number(source_id: str) -> int:
    """Return the number of a source id such as ``s07``."""
    return int(source_id[1:])


def passages_for_source(source_id: str, text: str, title: str, url: str, *, from_pdf: bool = False,
                        target: int = TARGET_WORDS, min_words: int = MIN_WORDS,
                        max_words: int = MAX_WORDS) -> List[dict]:
    """Clean and segment one source's text into corpus records (``id``, ``content``, provenance)."""
    n = source_number(source_id)
    return [
        {"id": f"s{n:02d}_p{k:02d}", "content": passage, "source_id": source_id, "title": title,
         "section": section, "url": url, "words": words(passage)}
        for k, (section, passage) in enumerate(
            segment(clean(text, from_pdf=from_pdf), target, min_words, max_words), start=1)
    ]
