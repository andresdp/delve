---
title: Cursor "Git at Any Scale" — Delve input corpus
description: A set of narrative markdown documents distilled from Cursor's "Git at any scale" blog post, organized as candidate input documents for Delve's grounded-theory / design-space pipeline.
source_article: https://cursor.com/blog/git-at-any-scale
generated: 2026-08-20
---

# Cursor "Git at Any Scale" — Delve Input Corpus

## What this is

This folder contains 16 short, self-contained markdown documents, each describing one topic, decision,
tradeoff, alternative, lesson, or evolutionary step surfaced by Cursor's engineering blog post
["Git at any scale"](https://cursor.com/blog/git-at-any-scale) (author: Vicent Martí, Cursor/Anysphere).
The post traces how Git repository hosting has been scaled — from GitHub's early filesystem experiments,
through GitHub's Spokes (three-phase-commit replication), Microsoft's client-side virtualization
(GVFS/Scalar), to Cursor's own **Continuity** system (a write-ahead log in S3) and its production
incarnation, **Origin**.

**This is analysis, not reproduction.** Every document below is written in original language that
paraphrases and interprets the source material — it does not quote the article at length. Facts,
numbers, and named systems are preserved faithfully; phrasing is not copied. A handful of documents
also draw on independent background sources (GitHub's own engineering blog, Microsoft's Git/Scalar
documentation) to add context the original post assumes as background knowledge — each such document
notes its extra sources explicitly. See `references.md` for the full source list.

**No design space was built here on purpose.** Per the request that produced this corpus, these
documents deliberately stop short of naming "dimensions," "values," or a taxonomy of architectural
alternatives. That synthesis step is left for Delve's own grounded-theory pipeline to perform once
these documents are fed in as its corpus — mining the dimensions is the point of the exercise, and
doing it by hand first would defeat it.

## How the documents are organized

The 16 documents are grouped into six folders that mirror the analytical lenses requested for this
corpus. The grouping is purely for human navigation — when preparing a Delve corpus, the folder
structure does not matter, only the flattened list of document contents does.

| Folder | Lens | Docs |
|---|---|---|
| `01-context/` | Why this problem exists and why it matters now | 2 |
| `02-past-decisions/` | Concrete architectural choices made, by whom, and when | 5 |
| `03-tradeoffs/` | Explicit costs accepted in exchange for a benefit | 3 |
| `04-alternative-solutions/` | Comparative framing across the different approaches considered | 2 |
| `05-lessons-learned/` | Generalizable takeaways the team names explicitly | 2 |
| `06-evolution/` | How the thinking and the architecture changed over time | 2 |

Every document uses the same shape: a short **Context** paragraph, the substantive narrative body, and
(where applicable) a closing note on what it implies or what tension it leaves unresolved — the same
kind of material Delve's example corpora (`examples/campus-bike`, `examples/pharmacy-food`) use as
individual "architecture decision" entries.

## Using this corpus with Delve

Delve's corpus loader (`main.load_corpus`, see `openwiki/pipeline/ingestion-and-preprocessing.md`)
accepts a single `.txt` file (one document per line) or a single `.json` file (an array of strings, or
of `{"content": "..."}` objects). It does not read a directory of `.md` files directly, so these 16
documents need to be flattened into one of those formats before running `main.py`.

A small, mechanical helper — `build_corpus.py`, included in this folder — does exactly that: it reads
every `.md` file here (skipping this README and `references.md`), strips the YAML frontmatter (folding
the title back in as a heading so it isn't lost), and writes
**`cursor_git_at_scale_documents.json`** — a flat JSON array of 16 plain strings, the same
top-level shape as `examples/campus-bike/campus_bike_architecture_decisions.json` and
`examples/pharmacy-food/pharmacy_food_architecture_decisions.json`. That file has already been generated
and sits alongside this README, ready for:

```
python main.py --corpus examples/cursor-git-at-scale/cursor_git_at_scale_documents.json \
               --config examples/cursor-git-at-scale/config.yaml \
               --output examples/cursor-git-at-scale/
```

Re-run `python build_corpus.py` any time after editing the `.md` files to regenerate it.
`--with-metadata` produces `{"id", "title", "content"}` objects instead, if you'd rather keep each
document's id/title addressable — still a valid Delve corpus, just a different shape than the sibling
examples.

**One difference worth flagging:** the sibling examples' arrays hold dozens of short, atomic,
single-decision strings (one pattern/choice per entry). This corpus instead holds 16 longer, multi-
paragraph write-ups — each one covers a whole decision, tradeoff, or lesson rather than a single
sentence-level choice. Delve's open-coding step will still run over each entry fine, but with fewer,
richer documents instead of many terse ones, which may shape what it saturates on. If you want closer
parity with the sibling examples' granularity (e.g. splitting each write-up into several atomic
decision-level strings), say so and that's a quick follow-up.

`build_corpus.py` and `config.yaml` are provided purely as packaging/plumbing — the config's `use_case`
field only orients the pipeline toward the domain (Git hosting infrastructure at scale), it does not
predefine any dimensions or values. Running Delve on the corpus file is the step that derives those.

## Files

```
01-context/
  context-why-git-is-hard-to-distribute.md
  context-ai-agents-and-the-forcing-function.md
02-past-decisions/
  decision-distributing-the-filesystem.md
  decision-distributing-a-key-value-store.md
  decision-github-spokes-consensus-replication.md
  decision-microsoft-gvfs-and-scalar.md
  decision-cursor-continuity-wal-in-s3.md
03-tradeoffs/
  tradeoff-three-phase-commit-tail-latency.md
  tradeoff-fixed-replica-floor-vs-agent-scale.md
  tradeoff-bandwidth-vs-cpu-in-compaction.md
04-alternative-solutions/
  alternative-solutions-comparative-overview.md
  alternative-azure-devops-hybrid-store.md
05-lessons-learned/
  lesson-repositories-as-pets-not-cattle.md
  lesson-strong-consistency-is-non-negotiable.md
06-evolution/
  evolution-from-consensus-to-append-only-log.md
  evolution-timeline-of-git-hosting-decisions.md
build_corpus.py
config.yaml
cursor_git_at_scale_documents.json   <- generated by build_corpus.py; the Delve corpus
references.md
```
