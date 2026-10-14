"""Plain-text extraction from local source files (HTML, PDF) and quality flags.

Moved from ``benchmark/fetch_sources.py``, which imports it back. No network access: the
user downloads the sources; this module only reads files.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlsplit

MIN_WORDS = 300  # below this, a text is flagged as "short" (likely partial)
BLOCK_MARKERS = {
    "paywall": ["member-only story", "sign up to read", "subscribe to continue", "become a member to read"],
    "bot_block": ["just a moment...", "attention required", "enable javascript and cookies",
                  "verify you are human", "access denied"],
}

# Sections that are not part of the source's argument (removed from the heading up to the
# next heading of the same or higher level). Reference lists and keyword/related blocks
# inject unrelated concepts that open coding would otherwise pick up.
NON_CONTENT_SECTION = re.compile(
    r"^(references?|bibliography|sources( ?& ?references)?|further reading|see also|"
    r"related (content|posts|articles|reading)|read next|more from\b.*|you may also like|tags|comments|"
    r".*keyword cluster.*)\s*:?$",
    re.I,
)
HEADING = re.compile(r"^(#{1,6})\s*\**(.+?)\**\s*$")


def trim_sections(text: str) -> Tuple[str, List[str]]:
    """Drop non-content sections (references, related content, SEO keyword lists, ...)."""
    out, removed, skip_level = [], [], None
    for line in text.splitlines():
        m = HEADING.match(line.strip())
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and NON_CONTENT_SECTION.match(title):
                skip_level = level
                removed.append(title)
                continue
        if skip_level is None:
            out.append(line)
    return "\n".join(out).strip(), removed


def _blocks_text(elements) -> str:
    parts = []
    for el in elements:
        for li in el.find_all("li"):
            li.insert_before("\n- ")
        parts.append(re.sub(r"\n\s*\n+", "\n\n", el.get_text("\n", strip=True)))
    return "\n\n".join(p for p in parts if p)


def _host(url: str) -> str:
    return (urlsplit(url).hostname or "") if url else ""


def site_extract(html: str, url: str) -> Optional[str]:
    """Site-specific extraction where generic main-text extraction loses content."""
    from bs4 import BeautifulSoup

    target = url.split("/web/", 1)[-1] if "web.archive.org" in _host(url) else url
    soup = BeautifulSoup(html, "lxml")
    if "stackexchange.com" in target or "stackoverflow.com" in target:
        # Question and all answers (generic extraction keeps only the question).
        posts = soup.select("div.s-prose") or soup.select("div.post-text")
        if posts:
            labelled = [("## Question" if i == 0 else f"## Answer {i}") + "\n\n" + _blocks_text([p])
                        for i, p in enumerate(posts)]
            return "\n\n".join(labelled)
    if "linkedin.com/pulse" in target:
        # Article blocks, including list items that generic extraction drops.
        body = soup.select_one('[data-test-id="article-content-blocks"]') or soup.select_one("article")
        if body:
            title = soup.select_one("h1")
            return ((f"# {title.get_text(strip=True)}\n\n" if title else "") + _blocks_text([body]))
    return None


def extract_html(html: str, url: str = "") -> str:
    """Return the main text of an HTML page as Markdown."""
    import trafilatura
    from bs4 import BeautifulSoup

    text = site_extract(html, url) or trafilatura.extract(
        html, output_format="markdown", include_comments=False,
        include_tables=True, favor_recall=True,
    ) or ""
    if len(text.split()) < MIN_WORDS // 2:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
            tag.decompose()
        fallback = re.sub(r"\n\s*\n+", "\n\n", soup.get_text("\n")).strip()
        if len(fallback.split()) > len(text.split()):
            text = fallback
    if "lesswrong.com" in url:
        # Keep the post; drop the comment thread and the karma/vote counters that follow it.
        lines = text.splitlines()
        cut = next((i for i, line in enumerate(lines) if line.strip() == "Comments"), len(lines))
        text = "\n".join(lines[:cut])
    return text.strip()


def extract_pdf(path: Path) -> str:
    """Return the text layer of a PDF: ``pdftotext`` when installed, else ``pypdf``.

    Scanned PDFs have no text layer and come out empty (no OCR); callers flag them.
    """
    if shutil.which("pdftotext"):
        # Reading order (no -layout): slide decks and multi-column PDFs come out as running text.
        out = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True)
        return out.stdout.strip()
    from pypdf import PdfReader

    return "\n\n".join((page.extract_text() or "").strip() for page in PdfReader(str(path)).pages).strip()


def clean_text(text: str) -> Tuple[str, List[str]]:
    """Trim non-content sections and collapse empty lines; return the text and removed section titles."""
    text, removed = trim_sections(text)
    # Collapse whitespace-only bullet lines ("- " followed by the item on the next line).
    text = re.sub(r"(?m)^-\s*\n(?=\S)", "- ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), removed


def quality_flags(text: str) -> List[str]:
    """Flag texts that are short (likely partial) or look like a paywall or bot block."""
    flags = []
    if len(text.split()) < MIN_WORDS:
        flags.append("short")
    low = text.lower()[:5000]
    for flag, markers in BLOCK_MARKERS.items():
        if any(m in low for m in markers):
            flags.append(flag)
    return flags


def extract_raw(raw_path: Path, url: str) -> Tuple[str, List[str]]:
    """Extract and clean the text of a saved raw file (HTML or PDF)."""
    if raw_path.suffix == ".pdf":
        text = extract_pdf(raw_path)
    else:
        text = extract_html(raw_path.read_bytes().decode("utf-8", errors="replace"), url)
    return clean_text(text)
