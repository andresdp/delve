#!/usr/bin/env python3
"""Download and extract the gray-literature sources of an ADD-Bench case.

Reads ``<case>/sources.csv`` and, for every source, downloads the page (or PDF),
stores the raw bytes under ``<case>/sources/raw/`` and an extracted plain-text
version under ``<case>/sources/text/``, and writes ``<case>/sources/manifest.json``
(+ ``manifest.csv``) with provenance and quality flags.

Fetch order per source:

1. ``fetch_override`` (when set), e.g. a raw PDF instead of a GitHub blob page.
2. ``archive_url`` (when set): the authors' own Wayback snapshot, fetched in
   raw mode (``id_``) so the Wayback toolbar is not part of the page.
3. ``url`` (live page).
4. Fallback: the closest Wayback snapshot of ``url`` (availability API).

Usage::

    python benchmark/fetch_sources.py                      # both cases (C1 and C2)
    python benchmark/fetch_sources.py benchmark/c1-ml-workflow
    python benchmark/fetch_sources.py benchmark/c2-rl-monitoring --only s3 s19 --force
    python benchmark/fetch_sources.py --reextract          # rebuild texts offline from raw files
    python benchmark/fetch_sources.py --from-manifest      # restore deleted downloads (same URLs/snapshots)

Requires: httpx, trafilatura, beautifulsoup4, lxml, and ``pdftotext`` (poppler).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx
import trafilatura
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
# The Wayback Machine rate-limits (429) browser-like agents but serves an
# identified research agent; live sites are fetched with the browser agent.
ARCHIVE_USER_AGENT = "delve-benchmark/0.1 (research; source recovery for ADD-Bench)"
MIN_WORDS = 300  # below this, a page is flagged as "short" (likely partial)
BLOCK_MARKERS = {
    "paywall": ["member-only story", "sign up to read", "subscribe to continue", "become a member to read"],
    "bot_block": ["just a moment...", "attention required", "enable javascript and cookies",
                  "verify you are human", "access denied"],
}
WAYBACK_RE = re.compile(r"^https?://web\.archive\.org/web/(\d+)(?:id_)?/(.+)$")


def raw_wayback(url: str) -> str:
    """Rewrite a Wayback URL to its raw (``id_``) form, without the toolbar."""
    m = WAYBACK_RE.match(url)
    return f"https://web.archive.org/web/{m.group(1)}id_/{m.group(2)}" if m else url


def closest_snapshot(client: httpx.Client, url: str) -> Optional[str]:
    """Ask the Wayback availability API for the closest snapshot of ``url``."""
    try:
        r, _ = fetch(client, str(httpx.URL("https://archive.org/wayback/available", params={"url": url})))
        snap = r.json().get("archived_snapshots", {}).get("closest")
        if snap and snap.get("available"):
            return snap["url"].replace("http://", "https://", 1)
    except Exception:  # noqa: BLE001 — fallback only
        pass
    return None


def fetch(client: httpx.Client, url: str, retries: int = 4) -> Tuple[Optional[httpx.Response], str]:
    """GET with backoff on rate limiting (429/503) and transient network errors."""
    err = ""
    for attempt in range(retries + 1):
        try:
            ua = ARCHIVE_USER_AGENT if "archive.org" in httpx.URL(url).host else USER_AGENT
            r = client.get(url, headers={"User-Agent": ua})
            if r.status_code not in (429, 503) or attempt == retries:
                return r, ""
            wait = float(r.headers.get("retry-after", 0) or 0) or 15 * (attempt + 1)
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
            if attempt == retries:
                return None, err
            wait = 10 * (attempt + 1)
        time.sleep(min(wait, 120))
    return None, err


def is_pdf(resp: httpx.Response, url: str) -> bool:
    ctype = resp.headers.get("content-type", "").lower()
    return "pdf" in ctype or url.lower().split("?")[0].endswith(".pdf") or resp.content[:5] == b"%PDF-"


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


def site_extract(html: str, url: str) -> Optional[str]:
    """Site-specific extraction where generic main-text extraction loses content."""
    host = httpx.URL(url).host if url else ""
    target = url.split("/web/", 1)[-1] if "web.archive.org" in host else url
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
        cut = next((i for i, l in enumerate(lines) if l.strip() == "Comments"), len(lines))
        text = "\n".join(lines[:cut])
    return text.strip()


def extract_pdf(path: Path) -> str:
    # Reading order (no -layout): slide decks and multi-column PDFs come out as running text.
    out = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True)
    return out.stdout.strip()


def clean_text(text: str) -> Tuple[str, List[str]]:
    text, removed = trim_sections(text)
    # Collapse whitespace-only bullet lines ("- " followed by the item on the next line).
    text = re.sub(r"(?m)^-\s*\n(?=\S)", "- ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), removed


def quality_flags(text: str) -> List[str]:
    flags = []
    if len(text.split()) < MIN_WORDS:
        flags.append("short")
    low = text.lower()[:5000]
    for flag, markers in BLOCK_MARKERS.items():
        if any(m in low for m in markers):
            flags.append(flag)
    return flags


def process(client: httpx.Client, row: Dict[str, str], out: Path, force: bool,
            prior: Optional[Dict] = None) -> Dict:
    sid = row["id"]
    raw_dir, text_dir = out / "raw", out / "text"
    existing = list(raw_dir.glob(f"{sid}.*"))
    if existing and (text_dir / f"{sid}.md").exists() and not force:
        return {"id": sid, "status": "skipped (exists)"}
    if prior and prior.get("via") == "manual":
        # Saved by hand from a browser: cannot be re-fetched automatically.
        return {**prior, "status": "needs manual save"}

    candidates: List[Tuple[str, str]] = []
    if prior and prior.get("fetched_from") and prior.get("status") != "failed":
        # --from-manifest: re-fetch exactly the URL recorded last time (same snapshot).
        candidates.append((prior.get("via") or "manifest", prior["fetched_from"]))
    if row.get("fetch_override"):
        candidates.append(("override", row["fetch_override"]))
        if row.get("archive_timestamp"):
            candidates.append(("override-archive",
                               f"https://web.archive.org/web/{row['archive_timestamp']}id_/{row['fetch_override']}"))
    if row.get("archive_url"):
        candidates.append(("archive", raw_wayback(row["archive_url"])))
    candidates.append(("live", row["url"]))

    attempts = []
    results = []  # successful candidates: (via, url, resp, ext, text, flags)
    for via, url in candidates + [("wayback-closest", None)]:
        if via == "wayback-closest":
            snap = closest_snapshot(client, row["url"])
            if not snap:
                attempts.append({"via": via, "url": None, "error": "no snapshot"})
                break
            url = raw_wayback(snap)
        resp, err = fetch(client, url)
        if resp is None or resp.status_code >= 400 or not resp.content:
            attempts.append({"via": via, "url": url, "status": getattr(resp, "status_code", None), "error": err})
            continue
        pdf = is_pdf(resp, url)
        if pdf:
            tmp = raw_dir / f".{sid}.tmp.pdf"
            tmp.write_bytes(resp.content)
            text = extract_pdf(tmp)
            tmp.unlink()
        else:
            text = extract_html(resp.text, url)
        text, _ = clean_text(text)
        flags = quality_flags(text)
        attempts.append({"via": via, "url": url, "status": resp.status_code, "words": len(text.split()), "flags": flags})
        results.append((via, url, resp, "pdf" if pdf else "html", text, flags))
        # Stop at the first clean result; otherwise keep trying the remaining candidates.
        if not flags:
            break

    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not results:
        return {"id": sid, "title": row["title"], "url": row["url"], "status": "failed",
                "attempts": attempts, "retrieved_at": retrieved, "notes": row.get("notes", "")}

    # Best candidate: no blocking flags first, then the most words.
    def rank(res):
        blocked = any(f in res[5] for f in ("bot_block", "paywall"))
        return (blocked, -len(res[4].split()))

    via, url, resp, ext, text, flags = min(results, key=rank)
    for old in raw_dir.glob(f"{sid}.*"):
        old.unlink()
    raw_path = raw_dir / f"{sid}.{ext}"
    raw_path.write_bytes(resp.content)
    text, removed = extract_raw(raw_path, url)
    write_text(text_dir / f"{sid}.md", row, url, via, retrieved, text)
    return {
        "id": sid, "title": row["title"], "url": row["url"], "fetched_from": url, "via": via,
        "http_status": resp.status_code, "content_type": resp.headers.get("content-type", ""),
        "raw_file": str(raw_path.relative_to(out.parent)), "text_file": f"sources/text/{sid}.md",
        "sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(), "words": len(text.split()),
        "flags": flags, "status": "ok" if not flags else "check", "retrieved_at": retrieved,
        "removed_sections": removed, "attempts": attempts, "notes": row.get("notes", ""),
    }


def extract_raw(raw_path: Path, url: str) -> Tuple[str, List[str]]:
    """Extract and clean the text of a saved raw file (HTML or PDF)."""
    if raw_path.suffix == ".pdf":
        text = extract_pdf(raw_path)
    else:
        text = extract_html(raw_path.read_bytes().decode("utf-8", errors="replace"), url)
    return clean_text(text)


def write_text(path: Path, row: Dict[str, str], url: str, via: str, retrieved: str, text: str) -> None:
    header = (f"# {row['title']}\n\n"
              f"- source_id: {row['id']}\n- original_url: {row['url']}\n- fetched_from: {url}\n"
              f"- via: {via}\n- retrieved_at: {retrieved}\n\n---\n\n")
    path.write_text(header + text + "\n", encoding="utf-8")


def reextract(row: Dict[str, str], out: Path, manifest: Dict[str, Dict]) -> Dict:
    """Rebuild the text of an already-downloaded source from its raw file (no network)."""
    sid = row["id"]
    entry = dict(manifest.get(sid, {}))
    raws = [p for p in (out / "raw").glob(f"{sid}.*") if p.suffix in (".html", ".htm", ".pdf")]
    if not raws:
        return {**entry, "id": sid, "status": entry.get("status", "failed")}
    raw = raws[0]
    if entry.get("status") == "failed" or not entry.get("fetched_from"):
        # A page saved by hand (e.g. from a browser) after a failed download.
        saved = datetime.fromtimestamp(raw.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
        entry.update(title=row["title"], url=row["url"], fetched_from=row["url"], via="manual",
                     http_status=None, content_type="", retrieved_at=saved,
                     raw_file=str(raw.relative_to(out.parent)), text_file=f"sources/text/{sid}.md")
    entry["sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    url = entry.get("fetched_from") or row["url"]
    text, removed = extract_raw(raw, url)
    write_text(out / "text" / f"{sid}.md", row, url, entry.get("via", ""), entry.get("retrieved_at", ""), text)
    flags = quality_flags(text)
    entry.update(id=sid, words=len(text.split()), flags=flags, removed_sections=removed,
                 status="ok" if not flags else "check")
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parent
    ap.add_argument("case_dirs", type=Path, nargs="*",
                    default=[here / "c1-ml-workflow", here / "c2-rl-monitoring"],
                    help="case directories containing sources.csv (default: C1 and C2)")
    ap.add_argument("--only", nargs="*", help="source ids to (re)fetch")
    ap.add_argument("--force", action="store_true", help="re-download even if files exist")
    ap.add_argument("--from-manifest", action="store_true",
                    help="re-fetch exactly the URL recorded in sources/manifest.json (same snapshot) before "
                         "falling back to the normal order; use to restore deleted downloads")
    ap.add_argument("--reextract", action="store_true",
                    help="no network: rebuild texts from the saved raw files (after changing the extraction)")
    ap.add_argument("--delay", type=float, default=5.0,
                    help="seconds between sources (the Wayback Machine allows ~15 requests/min)")
    args = ap.parse_args()

    for case_dir in args.case_dirs:
        print(f"== {case_dir.name}", flush=True)
        fetch_case(case_dir, args)
    return 0


def fetch_case(case_dir: Path, args: argparse.Namespace) -> None:
    rows = list(csv.DictReader(open(case_dir / "sources.csv", encoding="utf-8")))
    if args.only:
        rows = [r for r in rows if r["id"] in set(args.only)]
    out = case_dir / "sources"
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "text").mkdir(parents=True, exist_ok=True)

    manifest_path = out / "manifest.json"
    manifest = {e["id"]: e for e in json.loads(manifest_path.read_text())} if manifest_path.exists() else {}

    if args.reextract:
        for row in rows:
            entry = reextract(row, out, manifest)
            manifest[row["id"]] = entry
            print(f"{row['id']:>4}  {entry.get('status'):<8} {entry.get('words', ''):>6}  "
                  f"{','.join(entry.get('flags', []))}  removed={entry.get('removed_sections', [])}", flush=True)
        write_manifest(out, manifest)
        return

    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    with httpx.Client(headers=headers, follow_redirects=True, timeout=60) as client:
        for row in rows:
            prior = manifest.get(row["id"]) if args.from_manifest else None
            entry = process(client, row, out, args.force, prior)
            skipped = entry.get("status") in ("skipped (exists)", "needs manual save")
            if not skipped:
                manifest[row["id"]] = entry
                write_manifest(out, manifest)  # after every source, so interrupted runs keep their record
            print(f"{row['id']:>4}  {entry.get('status'):<17} {entry.get('via', ''):<16} "
                  f"{entry.get('words', ''):>6}  {','.join(entry.get('flags', []))}", flush=True)
            if not skipped:
                time.sleep(args.delay)


def write_manifest(out: Path, manifest: Dict[str, Dict]) -> None:
    ordered = sorted(manifest.values(), key=lambda e: int(e["id"][1:]))
    (out / "manifest.json").write_text(json.dumps(ordered, indent=2, ensure_ascii=False))
    with open(out / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["id", "status", "via", "words", "flags", "removed_sections", "http_status", "url",
                "fetched_from", "retrieved_at", "notes"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for e in ordered:
            w.writerow({**e, "flags": ";".join(e.get("flags", [])),
                        "removed_sections": ";".join(e.get("removed_sections", []))})

if __name__ == "__main__":
    sys.exit(main())
