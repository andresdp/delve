# ADD-Bench sources

Gray-literature corpora of the published Straussian-GT ADD studies used to evaluate Delve
(see `docs/paper/SANER2027_PAPER_PLAN.md`, §4 and backlog item B2).

| Case | Study | Sources | Where the URLs come from |
|---|---|---|---|
| `c1-ml-workflow/` | Warnett & Zdun, *Architectural Design Decisions for the Machine Learning Workflow* (IEEE Software, 2021/22) | 29 | Paper Table 1: `tinyurl.com/ml-adds-u1…u29`, each resolving to the authors' June 2021 Wayback Machine snapshot |
| `c2-rl-monitoring/` | Fang, Warnett & Zdun, *Architectural Design Decisions for Monitoring Deployed Reinforcement Learning Systems* (2026) | 29 | `**URL**` line of each source memo in the replication package (Zenodo 10.5281/zenodo.20305497, Apache-2.0), copied to `c2-rl-monitoring/replication_package/` |

The full list of URLs is in [`SOURCE_URLS.md`](SOURCE_URLS.md).

## Layout per case

- `sources.csv`: id, title, source type, paper class, original URL, archive URL/timestamp, fetch override, notes.
- `sources/raw/<id>.html|pdf`: downloaded bytes (gitignored).
- `sources/text/<id>.md`: extracted main text with a provenance header (gitignored).
- `sources/manifest.json` / `manifest.csv`: per-source provenance (fetched URL, via, HTTP status, SHA-256,
  word count, quality flags, all attempts).

## Re-creating the corpora

```bash
conda activate taxonomy   # needs httpx, trafilatura, beautifulsoup4, lxml + poppler's pdftotext
python benchmark/fetch_sources.py                       # both cases (C1, then C2)
python benchmark/fetch_sources.py benchmark/c1-ml-workflow   # one case only
# re-fetch selected sources:
python benchmark/fetch_sources.py benchmark/c2-rl-monitoring --only s19 --force
```

Fetch order: `fetch_override` → the authors' archived snapshot (raw `id_` mode) → live URL → closest
Wayback snapshot. Sources flagged `short`, `paywall` or `bot_block` in the manifest need a manual check.

## Verification status (2026-10-01)

Checks:
- expected title present;
- boilerplate and junk markers;
- for C2, presence of the analysts' quotes (the "Open Codes & Quotes" lines in `replication_package/memos/sNN.md`)
  in the downloaded text, scored fuzzily (at least 70% of a quote's content words present);
- manual skim of the beginning and end of every text.

| Case | Usable | Words (≈ tokens) | Notes |
|---|---|---|---|
| C1 | 29/29 | 70k (≈ 95k) | All from the authors' 2021 snapshots. s4 includes the full talk transcript. s8 (slides) is fragmented and partly marketing, but usable |
| C2 | 27/29 | 62k (≈ 84k) | 23 texts contain 100% of the analysts' quotes; s2, s27, s28 contain 80–92% (minor live-page drift). s3 and s16 were saved manually from a browser (`via: manual`) |

Cleanup applied by the extractor (re-run offline with `--reextract`):
- removed reference lists, "See also" / "Further reading", "Related content" blocks, and an SEO keyword appendix
  (C2 s4) (`removed_sections` in the manifest);
- dropped LessWrong comment threads (C2 s25, s26; all quotes are in the post body);
- added site extractors for StackExchange (question + answers, C2 s17) and LinkedIn (list items, C2 s19).

**Manual action needed (C2):**

| Source | Problem | Suggested fix |
|---|---|---|
| s5 (Medium) | 403 bot block; no Wayback snapshot (s3 and s16 already done manually) | Open in a browser and save the page (or copy the article text) as `sources/raw/sNN.html`, then run `--reextract --only sNN` |
| s10 (nexastack) | Live page gone (404); the Wayback copy is a redirect stub, so the text is empty | Retry with `--only s10 --force` once the Internet Archive CDX service is back (it was temporarily offline), or try archive.today |

Known content issue (left as is, because it is what the analysts coded): C2 s4 is machine-generated SEO content
(headings such as "(TABLE REQUIRED)").

## Caveats

- **C1 uses the authors' archived copies (2021)**: what the analysts saw.
- **C2 uses live pages (retrieved 2026-10)** with a Wayback fallback. The analysts coded them in early 2026,
  so pages may have changed since; compare against the memos in `replication_package/memos/` if in doubt.
- Source texts are third-party content: they are not committed, and only URLs and scripts are released.
