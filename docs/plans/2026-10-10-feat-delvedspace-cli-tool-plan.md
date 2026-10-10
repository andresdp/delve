---
title: "feat: DelveDSpace as a tool: ddspace workspace CLI, OKF wiki, agent queries"
type: feat
status: planned (not started; scope agreed 2026-10-10)
date: 2026-10-10
related: >-
  main.py, benchmark/{build_corpus,export_wiki,summarize_sources,design_points,describe_design_points,fetch_sources}.py,
  src/taxonomy_generator/wiki/, docs/DESIGN_SPACE_EXPLORATION.md §13 (wiki; §13.6 agent read access, WA1–WA4),
  docs/plans/2026-10-09-feat-wiki-ground-truth-overlay-plan.md (wiki modes, later)
---

# DelveDSpace as a tool

## Goal

A `ddspace` CLI that turns a folder of practitioner sources, downloaded by the user, into a design-space wiki that people
browse and coding agents query, and that the user can update later. Three uses:

1. **Mine:** set up a workspace and generate the design space (taxonomy).
2. **Publish:** build the wiki as an Open Knowledge Format (OKF v0.2) bundle plus the HTML site; update it later with
   user feedback or new sources.
3. **Consult:** people browse the HTML site or run `ddspace query`; agents read the OKF Markdown, run `ddspace query`
   (JSON), guided by a generated `AGENTS.md`.

## Decisions (user, 2026-10-10)

| # | Decision |
|---|---|
| D1 | `ddspace init` creates a default YAML config and asks a minimal set of questions interactively (LLM setup first). `ddspace wiki build` asks its own few questions the same way. |
| D2 | The CLI is built on **rich** (prompts, tables, progress, panels). |
| D3 | **No fetching from the internet.** The user downloads the sources; the tool imports local files. |
| D4 | Updating the design space has two modes: **feedback** (re-run seeded with the current design space plus the user's feedback) and **test** (dimensions frozen; new sources only add values). |
| D5 | The read command is `ddspace query` (not `q`). |
| D7 | The CLI uses **Typer** (help and errors rendered with rich). |
| D8 | **No built-in chat** (`ddspace ask`) in the first scope, and no MCP server. `ddspace query` offers specific, LLM-free operations over the wiki's concepts; a standard coding agent (Claude Code, Copilot) calls them and answers the user, as in llmwiki-cli. `ddspace ask` is deferred (see Later). |
| D9 | **Naming:** the tool is **DelveDSpace**; PyPI package `delvedspace`; CLI `ddspace` (second entry point `delvedspace`, same command). Not `delve` (the Go debugger, a PyPI package, and upstream Delve) and not `dspace` (the DSpace repository platform's command; taken on PyPI). Names checked free on PyPI, Homebrew and npm on 2026-10-10; check GitHub before publishing. |
| D6 | The wiki complies with OKF v0.2 (https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). |

## Out of scope

Experiments and ground-truth evaluation; an MCP server; a built-in chat (`ddspace ask`, deferred); editing the wiki by hand (pages are always rendered from a run); multi-user
hosting; internet fetching; ground-truth overlay and 2D/3D views (separate plans).

## Workspace layout

```
my-space/
  ddspace.yaml            # created by `ddspace init`: use case, models, pipeline, wiki settings
  .env                  # API keys (never committed; `init` writes or checks it)
  sources/              # the user's files: .md .txt .html .pdf (one file = one source)
  sources.csv           # optional metadata per file: id, file, title, url, type (init can draft it)
  corpus.json           # passages (built by `ddspace corpus`)
  runs/<timestamp>/     # every pipeline run (taxonomy JSON, report, logs)
  wiki/                 # current OKF bundle (Markdown) ← agents read this
  site/                 # HTML site (graph, tree)     ← people open this
  AGENTS.md             # how agents use wiki/ and `ddspace query`
  .gitignore            # sources/, corpus.json, .env, quotes if not shareable
```

`ddspace.yaml` is the existing config schema (`config.yaml`) plus a `workspace:` block (paths, current run) and a
`wiki:` block (export options), so `main.py --config ddspace.yaml` keeps working.

## Commands

| Command | Behavior | Built on |
|---|---|---|
| `ddspace init [dir]` | Create the layout and a default `ddspace.yaml`; interactive questions (below); `--yes` takes defaults for scripts/agents | new |
| `ddspace sources [scan]` | List the files in `sources/`, extract text (md/txt as is; html and pdf extracted), draft or check `sources.csv`, flag empty or very short files | `extract_html`, `extract_pdf` in `benchmark/fetch_sources.py` (moved into the package; no download code) |
| `ddspace corpus` | Split sources into passages → `corpus.json` | `benchmark/build_corpus.py` (generalized from `benchmark/<case>`) |
| `ddspace mine` | Run the pipeline into `runs/<ts>/`; shows a cost/size estimate and asks to confirm | `main.py` |
| `ddspace update --feedback "<text>" \| --feedback-file F` | Re-run in train mode seeded with the current run's design space and the feedback | `main.py --taxonomy … --feedback …` |
| `ddspace update --test [--sources NEW…]` | Test mode: dimensions frozen, new sources are classified and only add values | `main.py --mode test --taxonomy …` |
| `ddspace wiki build` | Export the current run: OKF bundle `wiki/` + `site/`; interactive questions (below); `--yes` for defaults | `benchmark/export_wiki.py`, `summarize_sources.py`, `design_points.py`, `describe_design_points.py` |
| `ddspace wiki update` | Re-export after `ddspace update`: diff against the previous run, write `log.md`, mark removed items `deprecated` | new (diff) + export |
| `ddspace wiki open` / `serve` | Open `site/index.html`, or serve it locally | new |
| `ddspace wiki check` | OKF conformance check of `wiki/` | new |
| `ddspace query <command> …` | Read-only queries over the current wiki, JSON by default, `--table` for people (rich) | WA1–WA2 (§13.6) |
| `ddspace agent setup [--claude] [--copilot]` | Write `AGENTS.md` (layout, `ddspace query` commands with examples, grounding rules); with `--claude`, a `CLAUDE.md` that imports it and an optional `.claude/settings.json` allow rule for `ddspace query`; with `--copilot`, `.github/copilot-instructions.md` pointing to it | WA3 |
| `ddspace reset [--wiki-only] [--purge] [--include-caches]` | Start over: archive (default) or delete the runs and the wiki, keep sources and settings; asks for confirmation (see below) | new |
| `ddspace mine --fresh` | Mine from scratch, ignoring the current run (no seeding); with `--reset`, runs `ddspace reset` first | `main.py` |
| `ddspace status` | Workspace state: sources, corpus, runs, current run, wiki freshness, next suggested command | new |

`ddspace query` is the interface for agents and people alike. Subcommands (from §13.6 WA2, plus `read` and `passage`):

| Subcommand | Returns |
|---|---|
| `info` | Run, use case, counts, core rule, inputs |
| `dims [--core]` | Dimensions with value counts, evidence, systems, core flag |
| `show <node>` | One concept (dimension, value, source, system, design point): fields, description, neighbors by edge type |
| `read <node>` | The concept's OKF page (Markdown), for full context |
| `values <dimension> [--stance accepted\|rejected\|mixed\|outcome]` | The dimension's values |
| `evidence <value> [--stance …] [--quotes]` | Supporting passage ids per source, with stance (quotes only if the wiki has them) |
| `passage <id>` | One passage's text and source (from the corpus; only where quotes are allowed) |
| `contested` | Mixed values with the passages on each side |
| `source <id>` | Values a source informs, with its stance on each |
| `system <code>` | The values a system takes per dimension (when a system map exists) |
| `relations [--from D] [--type T] [--depth N]` | Typed relations between dimensions |
| `path <a> <b>` | Shortest typed path between two concepts |
| `design-points [--dimension D]` | Sampled design points and their values |
| `search <text> [--kind K]` | Keyword match on labels and descriptions |

All are deterministic and make no LLM calls. Output is JSON by default (stable schema, for agents) and a rich table
with `--table` (for people). A node is accepted by id, slug or a unique label match; otherwise the command suggests
close matches and exits with code 2.

The old `delve = main:main` script entry is removed from `pyproject.toml` (no installed `delve` command); `main.py`
keeps working for the benchmark scripts.

## Interactive setup

Built with `rich.prompt` (`Prompt`, `Confirm`, `IntPrompt`) and rich panels; every question has a default, and
`--yes` (or a non-TTY) uses the defaults without asking.

**`ddspace init`** (minimal):
1. Workspace name.
2. Use case: one or two sentences (what design space, for whom).
3. LLM provider and models: generation, evaluation, embedding (default OpenAI: gpt-5.6-luna for all LLM roles,
   text-embedding-3-small). Check that the API key exists in the environment or `.env`; offer to write `.env`.
4. Sources folder (default `sources/`); report how many files it found.
5. Size of the design space: maximum number of dimensions (`max_num_clusters`, default none) and minibatch size.
6. Run the critic during mining? (evaluation on/off; off is cheaper).

Writes `ddspace.yaml` with comments for every option, prints the next commands.

**`ddspace wiki build`** (minimal):
1. Which run (default: current).
2. Include quoted passages? Warn that quotes copy source text; say no if the wiki will be shared publicly.
3. Generate source summaries? (one LLM call per source; show the count and confirm). Reuse stored summaries.
4. Design points: none / sample / sample and describe (descriptions cost one LLM call per point).
5. Core-dimension threshold: suggest a value from the distribution of sources per dimension (about a third of the
   sources), show how many dimensions would be core, let the user change it.
6. Freshness: refresh period for `stale_after` (default none).

Answers are saved in the `wiki:` block of `ddspace.yaml`, so later builds and `wiki update` do not ask again.

## OKF v0.2 compliance (bundle = `wiki/`)

Conformance requires: every non-reserved `.md` has YAML frontmatter with a non-empty `type`; `index.md` and `log.md`
follow §8 and §9 of the spec. Changes from today's export:

| Topic | Today | Change |
|---|---|---|
| `type` | `dimension`, `value`, `index`, … | Descriptive: `Design Decision`, `Design Alternative`, `Outcome`, `Source`, `System`, `Design Point`, `Overview`, `Approach` |
| `index.md` | Root page with run metadata in frontmatter | Listing per folder (`* [Title](path) - description`), no frontmatter except `okf_version: "0.2"` at the root; run metadata moves to `overview.md` |
| Links | Obsidian `[[wikilinks]]` in body and frontmatter | Markdown links, bundle-relative (`/concepts/x.md`); frontmatter holds paths |
| Provenance | Passage ids in body and frontmatter | `sources:` entries (`id`, `resource` = URL or the file path, `title`); evidence lines carry footnotes `[^s03]`; passage ids stay as an extension key |
| Trust | none | `generated: {by: delvedspace/<version> (<model>), at: <ISO time>}`; optional `ddspace wiki verify <page>` adds `verified: {by: human:<id>, at}` |
| `status` clash | Delve's `status` = stance (accepted/rejected/mixed/outcome) | OKF reserves `status` (draft/stable/deprecated): rename Delve's field to `stance`; use `deprecated` for items removed by an update |
| Updates | none | `log.md`, date headings (YYYY-MM-DD, newest first): added, changed, deprecated dimensions and values; optional `stale_after` |
| Bundle boundary | `wiki/`, `html/`, `raw/`, `SCHEMA.md` side by side | The bundle is `wiki/`; `site/` (HTML) and `raw/` (JSON for queries) stay outside it |

Effect: any OKF consumer (e.g. OpenWiki ≥ 0.2) can read the wiki. Obsidian still reads Markdown links. Optional later:
the core-dimension rule as an OKF Attested Computation concept.

## Demo scenario (C3, Git at scale)

The tool is demonstrated end to end on C3, whose sources are public:

1. `ddspace init git-at-scale`: answer the questions (use case, OpenAI models, sources folder, at most 5 dimensions).
2. Copy the five C3 source files (downloaded by the user) into `sources/`; `ddspace sources` lists and extracts them;
   `ddspace corpus` builds the passages.
3. `ddspace mine`: the estimate, the confirmation and the progress view; record cost and time.
4. `ddspace wiki build`: the questions (quotes, summaries, design points, core threshold); `ddspace wiki check`;
   `ddspace wiki open` to browse the overview, graph and tree views.
5. Optional: `ddspace update --feedback "…"` or `--test` with one extra source, then `ddspace wiki update` and `log.md`.
6. **Configure a coding agent:** `ddspace agent setup --claude --copilot`, open the workspace (or a project repo that
   contains it) in VS Code, and give the agent a design task, e.g. "Propose a replication design for our Git service,
   using the git-at-scale design space; cite which systems chose each option." Show it reading `AGENTS.md` and
   `wiki/index.md`, running `ddspace query`, and citing passage ids.
7. For people without an agent: the same lookups with `ddspace query … --table`.

The published C3 sample (GitHub Pages) is regenerated from this workspace once the OKF export lands.

## Reset and re-create from scratch

Useful after changing the use case, the models or major pipeline settings, or when updates have drifted: the user
wants a clean design space, not one seeded with the current run.

- `ddspace reset` shows what it will remove and what it keeps, then asks for confirmation (`--yes` skips the prompt for
  scripts).
  - **Removes:** `runs/`, `wiki/`, `site/`, the `raw/` query data, and the current-run pointer in `ddspace.yaml`.
  - **Keeps:** `sources/`, `sources.csv`, `corpus.json`, `ddspace.yaml` settings (including the wiki answers), `.env`,
    `AGENTS.md` and agent files.
  - **Keeps by default, because they cost LLM calls:** stored source summaries and LLM caches (e.g. judge caches).
    `--include-caches` removes them too. Design-point descriptions belong to a run and go with it.
  - **Archive by default:** everything removed is moved to `.ddspace/archive/<timestamp>/` (gitignored), so a reset can
    be undone by hand. `--purge` deletes instead, and asks again.
  - `--wiki-only` removes only `wiki/`, `site/` and `raw/`, keeping the runs (e.g. to rebuild the wiki with other
    options).
- `ddspace mine --fresh` mines from scratch without seeding from the current run; `ddspace mine --fresh --reset`
  resets first. Then `ddspace wiki build` as usual (its saved answers are reused).
- After a reset, `log.md` starts over with a "**Reset**" entry naming the archive folder; with `--purge` it only
  records the date.
- `ddspace status` shows archived resets.

## Update flow

1. `ddspace update --feedback …` or `ddspace update --test --sources new/*.pdf` → a new run in `runs/<ts>/`, recorded
   as current in `ddspace.yaml` (the previous run is kept).
2. `ddspace wiki update` → diff previous vs. current run by dimension and value ids and labels (added, changed,
   removed), re-export, append the diff to `log.md`, keep removed pages as `status: deprecated` for one update.
3. Test mode guarantees stable dimensions, so diffs are small; feedback mode may restructure, so the diff reports
   matched/unmatched dimensions by name and embedding similarity (reuse the consistency module's alignment).

## Work units

| Unit | Content | Effort |
|---|---|---|
| T1 | CLI skeleton on Typer and rich, workspace model, `init` with interactive setup, `status`; move text extraction and corpus building into the package | 2–2.5 d |
| T2 | `mine` (incl. `--fresh`), `update --feedback`, `update --test` as wrappers over the pipeline; cost/size estimate and confirm; `reset` | 1.5–2 d |
| T3 | `wiki build` with interactive setup; OKF compliance (table above); `wiki check`; `wiki open/serve` | 2 d |
| T4 | `wiki update`: run diff, `log.md`, deprecated pages | 1–1.5 d |
| T5 | Agent access: `raw/graph.json`, `ddspace query` commands, generated `AGENTS.md` (WA1–WA3) | 2–2.5 d |
| T6 | Packaging and docs: `pyproject` metadata and version, `pipx install`, README quickstart, a public sample workspace (C3 sample: public sources) | 1 d |

Total T1–T6: about 9.5–11.5 days. Reduced first version (if time is short): T1 without `status`, T2, T3, T4 with diff
only (no deprecated pages), T5, T6. About 7–8 days.

**Packaging:** `[project.scripts]` `ddspace` and `delvedspace` → the Typer app; `[project] name = "delvedspace"`.

**New dependency:** `typer` (add to `pyproject.toml`; in the existing conda env `taxonomy`: `pip install typer`).
rich is already a dependency.

## Branching and stabilization (not created yet)

All tool work happens off `main`, so `main` stays stable for the evaluation runs and the benchmark scripts. The
branches below are planned, not created; create them when the work starts.

- **Integration branch:** `feat/ddspace-tool`, created from `main`. It collects the tool work until it is stable.
- **Unit branches:** one short branch per work unit (`feat/ddspace-t1-cli`, `feat/ddspace-t3-okf`, …) created from
  `feat/ddspace-tool` and merged back into it when its tests pass. Small units may go directly on the integration branch.
- **Keeping up with `main`:** merge `main` into `feat/ddspace-tool` regularly (merge, not rebase: the repository sits in
  iCloud-synced storage and history is never rewritten). Pipeline or wiki fixes made for the evaluation land on `main`
  first and reach the tool branch through these merges.
- **What stays compatible:** `main.py`, `benchmark/*.py` and `config.yaml` keep working on the tool branch; the CLI wraps
  them. Code moved into the package (text extraction, corpus building, wiki export) keeps thin `benchmark/` entry points
  until the tool is merged.
- **Stable means** (all required before merging into `main`):
  - the full test suite passes, plus the new CLI tests;
  - the C3 demo scenario runs end to end in a fresh workspace (`ddspace init --yes` … `ddspace query`, and a coding agent answering a question with it);
  - `ddspace wiki check` passes on the C3 wiki, and the C1/C2 wikis still export;
  - `pipx install` from the branch works in a clean environment;
  - README quickstart and `USAGE.md` are updated.
- **Releases:** tag stable points on the branch (`ddspace-v0.1.0`, …); a demo or paper links a tag, not a moving
  branch. Merge into `main` after the first stable tag; later work continues on new feature branches.
- **Separate lines of work:** the wiki content modes (ground truth, overlay) and the evaluation-metrics plans have their
  own branches from `main`; they are not mixed into the tool branch. When both touch the wiki export, the first to merge
  into `main` wins and the other merges `main` in.

## Later (not in the first scope)

- `ddspace ask "<question>"`: a built-in chat that answers from the wiki with citations, an LLM agent whose only tools
  are the `ddspace query` functions. Deferred (2026-10-10): coding agents already provide this on top of
  `ddspace query`.
- An MCP server exposing the `ddspace query` functions (§13.6 WA4).

## Tests

- `init --yes` in a temp folder writes a valid `ddspace.yaml`; interactive prompts tested with scripted input.
- `sources` extraction for md/txt/html/pdf fixtures; `corpus` on fixtures.
- `wiki build` on the synthetic run of `test_wiki_export.py`: OKF conformance (every non-reserved `.md` has `type`;
  `index.md` format; links resolve), no passage text with quotes off.
- `wiki update`: diff and `log.md` on two synthetic runs.
- `reset`: in a temp workspace, the default archives runs and wiki and keeps `sources/`, `ddspace.yaml`, `.env`,
  `AGENTS.md` and caches; `--wiki-only`, `--include-caches` and `--purge` touch exactly their targets; `--yes` skips the
  prompt; nothing is touched when the user declines.
- `query`: one test per subcommand (WA2).
- `mine`/`update` wrappers: argument mapping to `main.py` (no LLM calls in tests).

## Open questions

- PDF extraction quality for user files (scanned PDFs are not supported; say so).
- Should `ddspace update --test` also accept feedback? (Today `--feedback` targets train-mode update/review prompts.)
- Where the workspace keeps run artifacts that are large (match files, html reports): keep, prune, or gitignore.
