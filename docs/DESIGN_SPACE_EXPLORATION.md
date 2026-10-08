---
title: Design Space Exploration — graph, wiki, query and CLI options
description: >-
  Options analysis for turning a Delve run into a navigable, queryable artifact (graph + wiki) with
  structural, search and natural-language queries from a CLI. Compares graph stores, wiki formats,
  search engines, query interfaces and integrated GraphRAG / LLM-wiki frameworks, and recommends a
  layered combination.
generated: 2026-10-02
updated: 2026-10-08
status: >-
  options analysis (§1–§12) plus a decided demo plan (§13, llmwiki-style wiki + graph site, paper
  figures); exporter, HTML pages and graph view built 2026-10-08 (§13.4); demo dry run and paper
  figures pending
related: >-
  docs/paper/SANER2027_PAPER_PLAN.md §6.5 (one-paragraph pointer; not in paper scope),
  CONCEPTS.md (Evidence Linking, Decision Status, Selected Dimensions, Grounded Theory Report)
---

# Design Space Exploration: graph, wiki, query and CLI options

## 1. Problem

A Delve run produces a design space that is really a graph: dimensions (decision points) own values
(candidate decisions or outcomes); values are supported by open codes, which come from passages, which
come from sources; passages accept or reject candidate decisions; dimensions relate to each other with
typed relations; and the run keeps a history of iterations, merges and dropped dimensions.

The current artifacts (Grounded Theory Report `.md`, Unified HTML Report, taxonomy JSON) render this as
lists and one relation diagram. They answer "what is in the design space?" but not exploratory questions
such as:

- Which candidate decisions are contested, and which sources take each side?
- What does source s07 contribute, and to which decision points?
- Why is this value here: which codes and passages support it, with what similarity?
- Which decision points does "Drift detection strategy" constrain, transitively?
- Which dimensions were merged or dropped, and why?
- How does this run differ from another run (or from the ground truth)?

Goal: export a run into a form that can be **browsed** (graph and pages), **queried exactly**
(structural queries), **searched** (keyword and semantic), and **asked in natural language**, all
from a CLI, without an LLM rewriting the design space.

## 2. Requirements

| # | Requirement | Why |
|---|---|---|
| R1 | **Fidelity**: the exported content is rendered from the run data, never reworded or re-extracted by an LLM | Same rule as the Grounded Theory Report; the design space is the research output |
| R2 | **Typed structure**: node types, edge types, status and stances are queryable properties, not free text | Questions like "mixed values per source" depend on them |
| R3 | **Traceability**: every answer can cite passage ids (and quote the passage) | Grounded theory audit trail; reviewers' first question |
| R4 | **CLI first**: every query mode works from a terminal and can emit JSON | Scripting, experiments, agent tool use |
| R5 | **Local and light**: no server or database daemon required for the default path; pip/npm installs only | Single-researcher setup, replication packages |
| R6 | **Natural-language questions** with cited answers | Exploration by people who did not run the pipeline |
| R7 | **Browsing / visualization** of the graph | The `.md`/`.html` reports cannot be navigated as a graph |
| R8 | **Multi-run**: several runs (seeds, cases, ground truth) side by side | Stability analysis, GT comparison |
| R9 | **Open licenses**, maintained projects | Artifact must be redistributable and reproducible |
| R10 | **Regenerable**: the export is a pure function of the run files, so it can be deleted and rebuilt | No hidden state; reruns overwrite cleanly |

## 3. What a run already contains

All from one run of `examples/cursor-git-at-scale` (`*_20261001_225321`), plus the benchmark metadata.

| File | Content relevant to the graph |
|---|---|
| `<name>_taxonomy_<ts>.json` | `selected_clusters` (dimensions with `id`, `name`, `description`, `relations[{target_id, type, rationale}]`, `values[{id, dimension_id, label, description, status, stances{accepted,rejected}, supporting_doc_ids, evidence_code_count, merged_from}]`, `evidence{codes, documents, sources}`, `unsupported_values`); `dropped_dimensions[{id, rationale}]`; `iterations[{explanation, clusters}]`; `saturation_history[{batch_index, is_saturated, coverage, codes, uncovered_concepts, rationale}]`; `evaluation`; `run_metrics` |
| `<name>_open_codes_<ts>.json` | `open_codes[{doc_id, label, rationale, status}]` |
| `<name>_documents_<ts>.json` | `documents[{id, content, summary, explanation, category, value, score}]` (single-label labeling) |
| `<name>_clusters_<ts>.json` | labeling view (dimension → labeled documents); redundant with the documents file |
| `benchmark/<case>/sources.csv` (C1/C2 only) | `id, title, source_type, paper_class, url, archive_url, …` per source `sNN` |
| `gt_model.json`, `gt_paper.json`, `gt_crosswalk.csv` (planned, B1) | ground-truth decisions, options, forces, decision links |

**Gaps to close before exporting:**

1. **Code → value edges are not saved.** `link_evidence` computes each code's assigned value and
   similarity (`evidence_linker.py`, `assign_codes`) but only keeps the resulting document ids. Persist
   the assignment (e.g. `value.evidence_codes: [{code_index, doc_id, similarity, status}]`, or a
   separate `<name>_evidence_<ts>.json`) so the graph can answer "why is this value here?".
2. **Open codes have no stable id.** Use `<doc_id>#<n>` (position within the document's codes) when
   writing the open-codes file.
3. **Sources only exist for passage corpora.** C1/C2 ids are `sNN_pKK`, so `source_of()` recovers the
   source. C3-raw (`examples/c3-git-at-scale/`, since 2026-10-08) uses the same ids. The curated C3 corpus
   uses document slugs, so each document is its own source. The exporter should accept an optional
   sources table and fall back to "document = source".
4. **Run identity.** Sibling artifacts are matched by timestamp; the export should record which files
   it was built from (`run.json` manifest) so R10 holds.

## 4. Target data model

One schema for all runs and for the ground truth.

**Nodes**

| Type | Id | Key properties |
|---|---|---|
| `Run` | `<name>@<ts>` | model, config hash, use case, metrics, mode |
| `Dimension` | `<run>/d<id>` | name (the decision question), description, evidence counts, selected / dropped, drop rationale |
| `Value` | `<run>/v<id>` | label, description, status (`accepted`/`rejected`/`mixed`/`outcome`), evidence_code_count |
| `Code` | `<run>/c/<doc_id>#<n>` | label, rationale, status |
| `Passage` | `<doc_id>` | text (or a pointer to it), summary, labeled dimension/value, score |
| `Source` | `sNN` | title, url, type, class |
| `GTDecision`, `GTOption`, `GTForce` | from `gt_*.json` | view membership (`paper+model` / `model only` / `paper only`) |

**Edges**

| Edge | From → To | Properties |
|---|---|---|
| `HAS_VALUE` | Dimension → Value | |
| `RELATES` | Dimension → Dimension | type (`constrains`, `precondition`, … ; `enables`/`complements` after P17), rationale |
| `ACCEPTS` / `REJECTS` | Passage → Value | from `stances` |
| `SUPPORTS` | Code → Value | similarity (needs gap 1) |
| `CODED_FROM` | Code → Passage | |
| `PART_OF` | Passage → Source | |
| `LABELED_AS` | Passage → Dimension / Value | score |
| `MERGED_FROM` | Value → (merged label), Dimension → Dimension | |
| `IN_RUN` | Dimension → Run | iteration / selected flag |
| `MATCHES` | Value → GTOption, Dimension → GTDecision | from the A1 matcher (later) |

Node ids are namespaced by run so several runs and the ground truth can live in one graph (R8);
`Passage` and `Source` are shared across runs of the same corpus.

Size, for scale: C2 has 243 passages, ~1–2k codes, tens of dimensions and a few hundred values, so
every option below handles it in memory; performance is not a selection criterion.

## 5. Architecture: compile once, query in layers

```
run files ──► [1 exporter: delve export] ──► <run>_design_space/
                                              ├── graph.json        (typed graph, node-link)
                                              ├── index.md, dimensions/, values/, sources/, runs/
                                              ├── AGENTS.md         (how to query this folder)
                                              └── run.json          (manifest of input files)
                     ┌──────────────┬──────────────┬───────────────┬──────────────┐
                     ▼              ▼              ▼               ▼              ▼
              [2 structural]   [3 search]    [4 natural lang.] [5 browse]   [6 adapters]
              delve graph …    QMD /         agent CLI /       Obsidian /   GraphML, LightRAG,
              graphify         llmwiki-cli   delve graph ask   d3 / graphify Neo4j, Cognee
```

Delve is the **compiler** in Karpathy's "LLM wiki" sense (raw sources → wiki → schema file), but a
deterministic one: the pages and the graph are rendered from the run data (R1). Every layer above
reads that folder; none writes back to it.

The rest of this document compares options per layer (§6), then integrated frameworks that try to be
several layers at once (§7), then recommends combinations (§8).

## 6. Options per layer

### 6.1 Layer 1 — graph store / serialization

| Option | What it is | Typed props (R2) | Query language | Footprint (R5) | License / status (R9) | Notes |
|---|---|---|---|---|---|---|
| **NetworkX node-link JSON** | `graph.json` loaded into NetworkX | yes | Python | none (already a dependency of many tools) | BSD | Native format for graphify; trivial to export to GraphML/GEXF for Gephi/Cytoscape. **Default.** |
| **SQLite tables** (`nodes`, `edges`, FTS5) | one `.db` file | yes | SQL + recursive CTEs | stdlib | public domain | Good for exact aggregates and joins; FTS5 gives keyword search for free; less natural for paths |
| **DuckDB** (+ DuckPGQ extension) | analytical SQL, property-graph queries via extension | yes | SQL / SQL:2023 PGQ | pip | MIT | Strong for cross-run analytics (seeds × cases); PGQ extension maturity to check |
| **Kùzu** (embedded Cypher) | embedded graph DB | yes | Cypher | pip | MIT, **repository archived Oct 2025**; forks LadybugDB, Bighorn | Was the natural embedded-Cypher choice; now a maintenance risk. Revisit LadybugDB only if Cypher is needed |
| **Neo4j / Memgraph** | graph database server | yes | Cypher | Docker server | Neo4j Community GPLv3 / Memgraph BSL | Best ad-hoc querying and visualization (Browser, Bloom); violates R5 for the default path. Good as an optional adapter |
| **RDF triples** (rdflib + SPARQL) | triples, ontology | yes (verbose) | SPARQL | pip | BSD | Expressive and standard, but heavier modeling and little tooling payoff here |

Recommendation: `graph.json` (node-link) as the canonical file; generate SQLite on demand inside the
CLI if aggregates get complex. Avoid a server in the default path.

### 6.2 Layer 1b — wiki page format

The same folder serves people (Obsidian, GitHub rendering) and agents (AGENTS.md + small pages).

| Convention | Layout | Fit |
|---|---|---|
| **Karpathy LLM-wiki layout** (raw / wiki / schema) | `wiki/` pages + one schema file telling the agent how to read and maintain the wiki | Conceptual model; the schema file becomes our `AGENTS.md` |
| **Obsidian vault** | any folder; `[[wikilinks]]`, YAML frontmatter, tags | Free browsing (graph view, backlinks), Dataview queries over frontmatter |
| **llmwiki-cli layout** | `raw/`, `wiki/entities`, `wiki/concepts`, `wiki/sources`, `wiki/synthesis`, auto `index.md`; pages = YAML frontmatter + markdown body; `[[wikilinks]]` | Maps cleanly: dimensions → `concepts/`, values → `entities/` (or `concepts/`), sources → `sources/`, run summary → `synthesis/`. Lets llmwiki-cli's search, backlinks, lint and orphans work unchanged |
| **OpenWiki layout** (`langchain-ai/openwiki`) | `index.md` + topic folders + `INSTRUCTIONS.md`, `okf_version` frontmatter | Built for code repositories (the repo's own `openwiki/`); the *shape* (index + small pages + instructions file) is worth copying, the generator is not applicable |

These conventions are compatible: a folder with `index.md`, `[[wikilinks]]`, YAML frontmatter and an
`AGENTS.md` is simultaneously an Obsidian vault, an llmwiki-cli wiki (if the subfolder names match) and
a Karpathy-style wiki. Choosing the llmwiki-cli folder names costs nothing and keeps that tool usable.

Example value page (frontmatter carries the queryable properties; body carries readable evidence):

```markdown
---
type: value
id: v2.1
dimension: "[[Repository Authority Architecture]]"
status: mixed
accepted_by: [404c2b5b, 478dc4e7, 644811ff, fb4cc0f0]
rejected_by: [308bf707]
evidence_codes: 6
merged_from: ["Consensus replication for repository hosting"]
qmd:
  metadata: {type: value, status: mixed, dimension: "Repository Authority Architecture"}
---
# Consensus-replicated repository storage

Repository state is maintained authoritatively across replicas coordinated through consensus.

## Adopted by
- [[s03]] · passage `s03_p02` — "…quote…" (code: *Consensus-before-action coordination*, sim 0.71)

## Rejected by
- [[s07]] · passage `s07_p01` — "…quote…"
```

Pages quote passages, so for C1/C2 the exported folder contains copyrighted source text: it must be
gitignored like the corpora (`examples/<case>/.gitignore`), and the replication package should ship
the exporter, not the export.

### 6.3 Layer 2 — structural queries (exact, no LLM)

| Option | How | Strengths | Weaknesses |
|---|---|---|---|
| **Own `delve graph` commands** over `graph.json` | Python (NetworkX), `--json` output | Exact; answers the fixed questions of §1 and all aggregates; the same functions become agent tools (§6.5) | Fixed question set; must be written and tested |
| **graphify** (`--graph <run>/graph.json`) | `explain`, `path`, `affected --relation R`, `query` (keyword + BFS), `tree` | Zero code; already installed and used in this repo. Tested on a toy design-space graph: `explain` lists typed incoming/outgoing edges, `path` returns typed paths (`s07_p01 --rejects--> value <--has_value-- dimension --constrains--> dimension`) | Built for code graphs: `affected` defaults to code relations (needs `--relation constrains`); `query` missed incoming `accepts`/`rejects` edges in the test; third-party dependency to pin |
| **Cypher** (Neo4j or a Kùzu fork) | load `graph.json`, query | Arbitrary ad-hoc queries | Server or archived engine; users must know Cypher |
| **SQL** (SQLite/DuckDB) | generated tables | Aggregates and cross-run joins; DuckDB for E-series analysis | Paths are awkward |
| **Obsidian Dataview** | queries over frontmatter in notes | Live tables inside Obsidian (e.g. all `mixed` values by dimension) | Only inside Obsidian; not CLI |

Sketch of the own commands (all with `--run <dir>` and `--json`):

```
delve export <taxonomy.json> [--sources benchmark/c2-rl-monitoring/sources.csv] [--gt gt_model.json]
delve graph dims                        # dimensions: values, evidence codes/docs/sources, relations
delve graph show <dimension|value>      # one node with its neighborhood and evidence quotes
delve graph evidence <value> [--stance accepted|rejected]
delve graph contested                   # mixed values with both sides' passages
delve graph source <sNN>                # decisions a source informs, with its stance on each
delve graph relations [--type constrains] [--from <dim>] [--depth N]
delve graph dropped                     # dropped dimensions, unsupported values, merges + rationale
delve graph diff <runA> <runB>          # recurring vs one-off dimensions (reuses consistency.py)
delve graph gt <run> --view paper|model # matched / missing / extra vs ground truth (after A1)
```

### 6.4 Layer 3 — search (keyword and semantic)

| Option | What | Fit |
|---|---|---|
| **QMD** (`tobi/qmd`, MIT, npm) | Local search engine over markdown collections: BM25 (`qmd search`), vector (`qmd vsearch`), hybrid with query expansion + LLM reranking (`qmd query`); `get`/`multi-get`; YAML metadata filters (`qmd:` key) with and/or/not; MCP server (stdio/HTTP) | Best fit. Runs fully locally (≈2 GB of small GGUF models downloaded on first use); no API key. Metadata filters cover status/type/dimension. Returns pages, not answers |
| **llmwiki-cli search** (MIT, npm, no LLM calls) | Full-text search over the wiki, JSON output; plus `links`, `backlinks`, `orphans`, `lint`, `status`, optional d3 graph page | Lighter than QMD (no models), keyword only. `lint`/`orphans` double as export checks (no value page without its dimension, no broken links). Young project (~100 stars); no import command, so check that it indexes pages written directly to disk rather than through `wiki write` |
| **Obsidian CLI** (official, ≥ 1.12) | `obsidian search`, `search:context`, tag and property filters, JSON output | Keyword/tag/property search only; needs the Obsidian app installed and the CLI enabled |
| **Own embedding index** | embed pages/passages with the run's embedding model (`text-embedding-3-small`) into SQLite/NumPy | Same embedding space as Delve's consolidation and evidence linking, so similarities are comparable with the pipeline's thresholds; needs an API key and some code |
| **ripgrep** | plain text search | Always available; what agents fall back to anyway |

### 6.5 Layer 4 — natural-language questions

| Option | How it answers | R1/R3 | Cost / effort | Notes |
|---|---|---|---|---|
| **Agent CLI in the folder** (e.g. `claude -p "…"`, other coding-agent CLIs) | Reads `AGENTS.md`, then pages, `graph.json`, and calls graphify / QMD / llmwiki-cli / `delve graph` as shell tools | Answers cite passage ids if `AGENTS.md` requires it; content stays read-only | Zero code beyond the export; per-question LLM cost | Fastest way to test whether NL answers are good enough. Reliable for explaining and reading; less reliable for exact aggregates (it may not scan every page) |
| **`delve graph ask`** (own LangGraph agent) | Tool-calling agent whose tools are the §6.3 functions + search; fixed system prompt; answers must cite passage ids | Same as above, plus validation of cited ids against the graph | 1–2 days; reuses Delve's model configuration | Can enforce "aggregates come from tools, not from reading"; can be evaluated with a small question set. Fits Delve's agentic framing |
| **MCP server over the export** | Expose the §6.3 functions and QMD search as MCP tools; any MCP client asks the questions | as above | small once §6.3 exists | QMD already ships an MCP server for the search half; community MCP servers for Obsidian vaults also exist (maintenance varies) |
| **Text-to-Cypher / text-to-SQL** (e.g. `neo4j-graphrag`) | LLM writes a query; DB executes it | exact when the query is right | needs the DB; prompt for the schema | Fails silently on complex questions (a wrong query returns a plausible wrong answer) |
| **LightRAG / Cognee query** | their retrieval modes + LLM answer | see §7 | see §7 | |

Rule for all NL options: **exact questions** (counts, "which dimensions have no rejected option",
"all sources that reject X") go to structural tools and are only phrased by the LLM; **explanatory
questions** ("why is consensus replication contested?") can be answered from pages and quotes.

### 6.6 Layer 5 — browsing and visualization

| Option | What you see | Notes |
|---|---|---|
| **Obsidian** graph view | notes as nodes, links as edges; local graph per note; colour by tag/folder; backlinks pane | Free; edges are untyped in the view (types live in page text and frontmatter); Dataview for tables |
| **graphify** `tree` / `cluster-only` | D3 collapsible tree and `graph.html` with communities | Zero code given `graph.json`; community detection may group decision points meaningfully |
| **llmwiki-cli** d3 graph | force-directed graph page (publishable on GitHub Pages) | Comes with the wiki layer |
| **GraphML → Gephi / Cytoscape** | full control of layout, typed edge styling, filters | Best for paper figures (e.g. sources × contested decisions) |
| **LightRAG web UI** | knowledge-graph explorer and query debugging | Only if the LightRAG adapter is built |
| **Neo4j Browser / Bloom** | typed, styled, interactive | Server required |
| **Unified HTML Report** (existing) | one page, lists and one relation diagram | Could embed a small force graph later, but it stays a report, not an explorer |

### 6.7 Layer 6 — adapters (optional exports from `graph.json`)

GraphML/GEXF (Gephi, Cytoscape); LightRAG `insert_custom_kg` payload; Neo4j CSV import; Cognee
`DataPoint`s. Each is a small mapping function from the canonical graph; none is the source of truth.

## 7. Integrated frameworks (several layers in one)

| Framework | Ingestion model | Can it take Delve's graph as is? | Fit | Verdict |
|---|---|---|---|---|
| **LightRAG** (`HKUDS/LightRAG`, MIT) | LLM extracts entities/relations from chunks; also `insert_custom_kg({chunks, entities, relationships})` with `content/source_id/file_path`, `entity_name/entity_type/description/source_id`, `src_id/tgt_id/description/keywords/weight/source_id` | Yes, via `insert_custom_kg` | Query modes local/global/hybrid/naive/mix; `lightrag-server` with web UI and graph explorer; storage from NetworkX to Neo4j/Postgres | **Adapter only.** Entities are keyed by normalized `entity_name`, so equal value labels in different dimensions collide (qualify as `Dimension :: Value`); edge types, status and stances become description/keyword text (R2 lost); every answer is LLM-generated; inserting ordinary documents later mixes LLM-extracted entities into the curated graph |
| **Cognee** (`topoteretes/cognee`) | "cognify" pipeline extracts a graph; custom typed nodes/edges can be defined as Pydantic `DataPoint`s and added directly | Yes, with custom `DataPoint` models (check current API) | Graph + vector stores, search types, CLI | Typed custom ingestion fits R2 best of the frameworks, but it is heavy for this use (several stores, pipeline concepts, configuration); keep as a fallback if the light stack falls short |
| **OpenKB** (`VectifyAI/OpenKB`, Apache-2.0) | LLM compiles documents into a wiki (summaries, concept pages, entity extraction, cross-links); PageIndex tree retrieval, no vector DB; `openkb query`, `openkb chat`, web UI, REST | No: the LLM decides pages and links | Good CLI and UX | **Not suitable as the store** (breaks R1: it would re-summarize Delve's pages). Its interaction design (`query` with citations, `chat`) is a good model for `delve graph ask` |
| **Other LLM-wiki apps** (`ddsyasas/llm-wiki`, `nvk/llm-wiki`, `mindbase-llm-wiki`, `obsidian-llm-wiki`, `llm-wiki-compiler` Claude Code plugin) | LLM compile step is the main feature | Only as "raw" input, which they rewrite | Varying UIs, MCP servers | Same problem as OpenKB (R1). Useful as references for page conventions and agent schema files |
| **rust-llm-wiki** (`joshgarnett/rust-llm-wiki`) | CLI wiki with semantic search, traceable sources, research workflows; Obsidian-compatible pages; `source add` imports files | Partly (imports files) | Close in spirit to the light stack | **No license declared** (fails R9); revisit if that changes |
| **Microsoft GraphRAG** | own indexing pipeline (entity extraction, community reports) | Not without fighting the pipeline | Strong global summarization | Heavy and extraction-centric; not a fit |
| **OpenWiki** (`langchain-ai/openwiki`) | agent-generated code wiki for a repository | No (code-oriented) | Used in this repo for code | Copy its shape (index, small pages, instructions file), not the tool |

## 8. Comparison and recommended combinations

How well each stack covers the requirements (● full, ◐ partial, ○ no):

| Stack | R1 fidelity | R2 typed | R3 trace | R4 CLI | R5 light | R6 NL | R7 browse | R8 multi-run | R9 open |
|---|---|---|---|---|---|---|---|---|---|
| **A. Minimal**: export + `delve graph` + agent CLI | ● | ● | ● | ● | ● | ◐ | ○ | ● | ● |
| **B. Light wiki stack**: A + wiki pages + QMD + graphify + Obsidian | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| **B′. Light wiki stack with llmwiki-cli** instead of QMD | ● | ● | ● | ● | ● | ◐ | ● | ● | ● |
| **C. LightRAG** (custom KG) | ◐ | ○ | ◐ | ◐ | ◐ | ● | ● | ◐ | ● |
| **D. Neo4j + text-to-Cypher** | ● | ● | ◐ | ◐ | ○ | ◐ | ● | ● | ◐ |
| **E. Cognee** (custom DataPoints) | ● | ● | ◐ | ● | ○ | ● | ◐ | ● | ● |
| **F. OpenKB / LLM-wiki apps** | ○ | ○ | ◐ | ● | ● | ● | ● | ◐ | ● |

**Recommendation: stack B, keeping B′ open.**

1. **Exporter** (`delve export`): `graph.json` + wiki pages in llmwiki-cli-compatible folders +
   `AGENTS.md` + `run.json`. Closes gaps 1–4 of §3.
2. **Structural CLI** (`delve graph …`): the fixed questions and aggregates; graphify for
   `explain`/`path`/`affected` without extra code.
3. **Search**: QMD by default (hybrid search and metadata filters, MCP). **llmwiki-cli stays an
   option** for the wiki layer: no models to download, link analysis (`backlinks`, `orphans`), `lint`
   as an export check, and its own d3 graph page. The two are not exclusive: QMD indexes any markdown
   folder, and llmwiki-cli works on the same folder if its layout is used.
4. **Natural language**: first an agent CLI in the folder guided by `AGENTS.md`; then `delve graph ask`
   if answers need enforced citations or evaluation.
5. **Browse**: Obsidian on the same folder; GraphML for paper figures.
6. **Adapters** (LightRAG, Neo4j, Cognee) only if a specific need appears (e.g. a web UI for others).

Decision points between QMD and llmwiki-cli:

| If you need… | Choose |
|---|---|
| semantic / hybrid search, metadata filters, MCP | QMD |
| no model downloads, backlinks/orphans, wiki lint, a publishable graph page | llmwiki-cli |
| an agent that also *maintains* notes (e.g. analyst memos on top of the export) | llmwiki-cli (its write/lint commands), keeping Delve-generated pages read-only |

## 9. Question catalog → which layer answers it

| Question | Layer | Example |
|---|---|---|
| List decision points with evidence counts | structural | `delve graph dims` |
| Contested decisions and who takes each side | structural (+ quotes from pages) | `delve graph contested` |
| What does source s07 contribute? | structural | `delve graph source s07` |
| Why is value X in the design space? | structural + pages | `delve graph evidence "X"` / `graphify explain "X"` |
| How does dimension A affect B? | structural | `graphify path "A" "B"`, `delve graph relations --from A --depth 2` |
| Which decisions concern rollback or recovery? | search | `qmd query "rollback recovery" ` with `type: value` |
| What was merged or dropped, and why? | structural | `delve graph dropped` |
| Which GT options did Delve miss (paper view)? | structural (after A1) | `delve graph gt <run> --view paper` |
| Summarize the trade-offs around consensus replication | NL | agent CLI / `delve graph ask` |
| Compare two seeds' design spaces | structural | `delve graph diff runA runB` |

## 10. Implementation sketch and effort

| Step | Content | Effort |
|---|---|---|
| 0 | Persist code → value assignments and code ids in the open-codes/evidence output (gaps 1–2) | 0.5 d |
| 1 | `delve export`: canonical graph (`graph.json`), run manifest, sources table input | 0.5–1 d |
| 2 | Wiki pages + `index.md` + `AGENTS.md` (templates, deterministic), llmwiki-cli folder names, gitignore rule | 0.5–1 d |
| 3 | `delve graph` structural commands with `--json`; unit tests on a synthetic run (like `conftest.py` fixtures) | 1–1.5 d |
| 4 | Try graphify, QMD, llmwiki-cli, Obsidian on a C3 and a C2 export; note what works | 0.5 d |
| 5 | NL: agent CLI trial with a 10–20 question set (§9); decide whether `delve graph ask` is needed | 0.5 d |
| 6 | Optional: `delve graph ask`, GraphML/LightRAG adapters, GT import | 1–3 d |

Steps 0–3 are useful on their own (exploring C1–C3 outputs), and step 0 also benefits evaluation
(evidence provenance for M-protocol audits).

## 11. Risks and open questions

- **Staleness**: the export is a snapshot; rebuild on every run (R10). Never hand-edit exported pages;
  analyst notes go in a separate folder that links into them.
- **Copyright**: exported pages quote corpus passages; C1/C2 exports must stay out of git.
- **Untyped links in wiki tools**: Obsidian and llmwiki-cli treat `[[links]]` as untyped; types
  must stay in frontmatter and `graph.json`, and structural questions must use those.
- **NL answer quality**: needs a small question set with expected answers before claiming anything;
  aggregates must come from tools.
- **Third-party maturity**: llmwiki-cli is young; graphify is code-oriented; QMD downloads models.
  Pin versions; keep the exporter and `delve graph` free of hard dependencies on them.
- **Which view to export**: `selected_clusters` by default; `--iteration N` and `--all-dimensions`
  (including dropped) as flags, matching the Grounded Theory Report's explicit-view rule.
- **Multi-run graphs**: namespacing by run id is simple; cross-run alignment edges come from
  `consistency.py` (and GT `MATCHES` from the A1 matcher), not from the exporter.
- **Open**: should values that are outcomes become a separate node type (closer to GT forces)? Decide
  together with the P17 relation redesign.

## 13. Decided demo plan (2026-10-08): llmwiki-style wiki and graph site

**Status:** decided with the user on 2026-10-08, to be built on its own feature branch based on `feat/c3-git-at-scale`, which holds the C3 run and its design points. It narrows §8 stack B to its browse and visualize slice for two uses:
- a demo of one run's taxonomy at a meeting;
- a few figures for the paper.

Search, natural-language questions, the `delve graph` CLI and adapters stay out of scope (§6.3–6.7). The deferred decision-focus pass (`docs/plans/2026-10-08-1500-feat-decision-focus-pass-plan.md`) is separate and does not block this.

**Model, not dependency.** The idea comes from the LLM-wiki pattern and llmwiki-cli in particular. Its sample wiki is `test-wiki-page/` in `doum1004/llmwiki-cli`, and its published page is <https://doum1004.github.io/llmwiki-cli/>:
- a folder of small markdown pages with frontmatter and `[[wikilinks]]`, grouped into a few shelves;
- a d3 force graph with nodes colored by shelf and sized by connectivity;
- a search box and a reader panel.

We reuse the idea and keep the folder compatible, but the **default build relies on nothing from llmwiki-cli**: our exporter writes the pages, the HTML wiki and the graph page itself. Using llmwiki-cli's own tools on the same folder (`wiki lint`, `orphans`, its d3 site scripts) stays an **option** (D3).

### 13.1 Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | **One deterministic exporter** writes a wiki in the llmwiki-cli layout: `.llmwiki.yaml`, `SCHEMA.md` (our `AGENTS.md`), `raw/` (the run manifest) and `wiki/` with `index.md`, `concepts/`, `entities/`, `sources/`, `synthesis/`. Pages carry YAML frontmatter and `[[wikilinks]]`. | The same folder works as an Obsidian vault and as an llmwiki-cli wiki, at no extra cost. R1: every page is rendered from run data by templates, with no LLM call. |
| D2 | **Shelf mapping:**<br>- `concepts/` = dimensions (decision points);<br>- `entities/` = values (candidate decisions and outcomes);<br>- `sources/` = corpus sources (`sNN`, from `benchmark/<case>/sources.csv`);<br>- `synthesis/` = generated overviews (run summary, contested decisions, dropped dimensions and, for C3, one page per system plus the system × dimension matrix);<br>- `designs/` = sampled design points, only when given (D11). | Shelves become the node kinds of a design space. Passages are not pages (too many nodes). Their quotes appear inside value pages. |
| D3 | **Graph page: our own, the llmwiki-cli site as an option.**<br>- **Default:** the exporter writes `html/graph.html`, a `jinja2` template with a d3 force graph in the llmwiki-cli style (shelf colors, size by connectivity, search, click to open the page).<br>- **What our own page adds:**<br>&nbsp;&nbsp;- node color by status for values (accepted, rejected, mixed, outcome);<br>&nbsp;&nbsp;- edge styles by type (has-value, relation type, accepts/rejects, in-design-point);<br>&nbsp;&nbsp;- filters by shelf and status;<br>&nbsp;&nbsp;- the optional design-point layer (D11);<br>&nbsp;&nbsp;- clicking a node opens its HTML page (D10).<br>- **Option:** run llmwiki-cli's generated `build-graph` and `build-site` scripts (`bun run scripts/generate-viz-scripts.ts`, needs Bun or Node ≥ 18) on the same `wiki/` folder for the stock look. | Owning the graph page removes the Node/Bun dependency from the main path and gives the typed edges and status colors the stock site lacks (it colors by folder and draws untyped links). Keeping the layout compatible leaves the stock site one command away. |
| D4 | **Offline:**<br>- d3 is vendored into `html/assets/`;<br>- the graph data is inlined in `graph.html`, not fetched.<br><br>Everything opens from `file://`, with no server and no internet. | Meeting rooms may have no internet. If the optional llmwiki-cli site is used, its CDN imports are rewritten to local files the same way. |
| D5 | **Status encoding:** a value page's frontmatter and tags carry `status` (accepted / rejected / mixed / outcome); HTML pages and the graph color by it. | Status is the most informative property of a value. |
| D6 | **Design-point pages** (only with D11):<br>- `synthesis/design-points.md`: one section per group (attested by system, novel, control) and the sampler's diagnostics;<br>- `designs/<point-id>.md`: one page per point, a table of dimension → value with `[[links]]`, its group and, for attested points, its system. | Shows the design space being used to compose designs, which is a paper contribution. No judge verdicts yet (A13 is not built); a verdict field is added when they exist. |
| D7 | **Copyright:** value pages quote passages. Then:<br>- C1, C2 and C3-raw exports are gitignored like the corpora and never published publicly;<br>- an exporter flag `--no-quotes` writes passage ids only, for a site that can be published (e.g. GitHub Pages);<br>- the curated C3 corpus is an LLM-assisted paraphrase (not the source text), so a curated export may carry quotes. | Same rule as the corpora (§6.2). |
| D8 | **Paper figures are separate from the site:** static SVG/PDF from Python (matplotlib, already installed), generated from the same run data:<br>(a) design-space overview: dimensions with their values colored by status, plus the relations between dimensions;<br>(b) C3 system × dimension matrix (Shaw's Table 1), from `benchmark/c3-git-at-scale/passage_systems.csv` (primary system) and each value's `supporting_doc_ids`;<br>(c) C1/C2 ground-truth comparison (matched / missed / extra), from the matcher outputs (`*_gt_match.json`, `*_gt_alignment.csv`, `*_gt_metrics.json`). | A force-directed web graph is not a print figure. Figures must be reproducible from the run files. |
| D9 | **Demo content:** one run's taxonomy, no ground truth. Default: the C3 run `examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350.json`, with its design points and the B7 system pages. C1 or C2 work with the same exporter. | The C3 story (GitHub, Google, Microsoft and Cursor as points in one space) is the clearest for a non-specialist audience. |
| D10 | **Every wiki page is also written as an HTML file**, next to the markdown:<br>- **rendering:** the exporter renders each page with `markdown-it-py` and `jinja2`, both already in the `taxonomy` env, and turns `[[wikilinks]]` into relative links to the `.html` pages;<br>- **page chrome:** a shared stylesheet; a sidebar listing the shelves; frontmatter shown as a property table (type, status, dimension, stances, systems); status badges;<br>- **graph link:** each page links to `graph.html`, opened on its node;<br>- **output:** a self-contained static wiki (`html/`) that works from `file://` and can be zipped or shared as one folder. | Pages open with a double click and can be shown or screenshotted one by one. Rendering from the same page sources keeps markdown and HTML identical in content (R1, R10). |
| D11 | **Design points are optional everywhere.** The exporter takes `--design-points <*_design_points.json>`.<br>- **Without it:** no `designs/` shelf, no design-point page, no layer in the graph, and no link to any of them. The wiki and graph are complete on their own.<br>- **With it:** the D6 pages are written.<br>- **Graph layer:** each design point becomes a node on its own shelf, linked to the values it combines, colored by group (attested, novel, control).<br>- **Toggle:** the layer is off by default and shown with a checkbox; it can be filtered by group and by k.<br>- **Point view:** selecting a point highlights its values and their dimensions. | Sampling design points is a separate, optional step (A12), and with 2 × 90 points the graph would be crowded if always on. A toggle lets the demo show the space first and then "compose a design" in it. |

### 13.2 Export layout for one run

```
<run>_wiki/                          (gitignored when pages quote passages; D7)
├── .llmwiki.yaml                    name: <case>-<ts>, domain: design-space, paths: raw/wiki/SCHEMA.md
├── SCHEMA.md                        how the wiki is organized; read-only, generated (R1)
├── raw/run.json                     input files (taxonomy, corpus, sources, system map, design points),
│                                    taxonomy view, exporter version (R10)
├── wiki/                            markdown pages (Obsidian / llmwiki-cli compatible)
│   ├── index.md                     run summary, use case, links to every shelf
│   ├── concepts/<dimension-slug>.md question, description, evidence counts, values by status, relations
│   ├── entities/<value-slug>.md     dimension, status, stances, supporting passages + quotes, merged-from
│   ├── sources/sNN.md               title, url, type; decisions it informs, with its stance on each
│   ├── synthesis/
│   │   ├── overview.md              all dimensions and values in one table
│   │   ├── contested.md             mixed values with both sides
│   │   ├── dropped.md               dropped dimensions, unsupported values, rationales
│   │   ├── design-points.md         only with --design-points (D6, D11)
│   │   ├── systems/<system>.md      C3 only: the option each system takes per dimension (B7)
│   │   └── system-matrix.md         C3 only: system × dimension table
│   └── designs/<point-id>.md        only with --design-points (D6, D11)
├── html/                            the same pages as static HTML (D10), plus:
│   ├── graph.html                   our d3 graph page, data inlined (D3, D4, D11 layer)
│   └── assets/                      style.css, d3.min.js (vendored)
└── dist/                            optional: llmwiki-cli's stock site (D3 option)
```

Example frontmatter of a value page:

```yaml
---
title: "Write-ahead log in object storage"
type: value
status: accepted
dimension: "[[concepts/authority-synchronization]]"
accepted_by: [s01_p10, s01_p11]
rejected_by: []
systems: [CUR-CONT]          # C3 only, from B7 (primary system)
design_points: [P012, P047]  # only with --design-points
tags: [value, accepted, authority-synchronization]
---
```

### 13.3 Work units (for the feature branch)

| Unit | Content | Effort |
|---|---|---|
| W1 | Exporter, library plus CLI (`benchmark/export_wiki.py`, or `main.py --export-wiki`):<br>- inputs: a run's taxonomy JSON; optionally the corpus (for quotes), `sources.csv`, a B7-style system map and `--design-points`;<br>- output: the `wiki/` part of §13.2 and `raw/run.json`;<br>- deterministic: the same inputs give byte-identical pages;<br>- flags: `--no-quotes`, `--view selected/final`;<br>- unit tests on a synthetic run: slugs unique; every `[[link]]` resolves; no LLM call; quotes omitted under `--no-quotes`; without `--design-points`, no design-point page or link exists. | 1 d |
| W1b | HTML rendering of the wiki (D10):<br>- one `jinja2` page template plus a stylesheet;<br>- `markdown-it-py` for the body, with `[[wikilinks]]` rewritten to relative `.html` links;<br>- property table and status badges;<br>- unit tests: every link in `html/` resolves to an existing file; markdown and HTML pages have the same links; same output on a re-run. | 0.5 d |
| W2 | Graph page (D3, D4, D11):<br>- `html/graph.html` from a `jinja2` template with vendored d3 and inlined node-link data (typed edges, shelf, status, group);<br>- shelf and status colors, size by connectivity, search, click-through to pages, filters;<br>- the optional design-point layer with its toggle and highlight;<br>- tests on the data builder: node and edge counts match the taxonomy; edge types are present; design-point nodes appear only when given. | 1 d |
| W3 | Synthesis pages (overview, contested, dropped; C3 system pages and matrix) and design-point pages (D6), inside the exporter. | 0.5 d |
| W4 | Demo dry run:<br>- export C3 with design points, and one of C1/C2 without;<br>- open the HTML wiki and the graph offline (`file://`);<br>- prepare a short click path: index → a contested decision → a system page → turn on design points → an attested and a novel point;<br>- fix what looks wrong. | 0.25 d |
| W5 | Paper figures (D8 a–c) as a script writing SVG/PDF to `docs/paper/figures/`. Can follow the demo. | 1 d |
| W6 (optional) | llmwiki-cli's stock site and checks on the same folder: `wiki lint`, `wiki orphans`, and its `build-graph`/`build-site` with imports made local. | 0.25 d |

**To install** (no new Python environment): nothing for W1–W5. `jinja2`, `markdown-it-py` and `matplotlib` are already in the `taxonomy` env; d3 is a single vendored file (downloaded once from cdnjs or jsDelivr and kept in the repo with its ISC license). W6 only: Bun or Node ≥ 18 (for example `brew install oven-sh/bun/bun`) and `npm install -g llmwiki-cli`.

### 13.4 Built (2026-10-08, branch `feat/design-space-wiki`)

W1, W1b, W2 and W3 are implemented:
- **Code:** `src/taxonomy_generator/wiki/` (data model, renderer, templates) and the CLI `benchmark/export_wiki.py`.
- **Tests:** `tests/unit_tests/test_wiki_export.py`.
- **C3 system names:** `benchmark/c3-git-at-scale/systems.csv`.

Differences from the plan:
- System pages appear only for systems with evidence in the exported run. The system matrix shows at most three options per cell; the full list is on each system's page.
- In the graph, sources and systems start hidden (their evidence edges crowd the default view), and so does the design-point layer.
- Revised 2026-10-08 after a first look:
  - pages say **values** (Delve's term), not "options";
  - table cells with several entries are bulleted lists;
  - the graph layout is compact and is computed before drawing, then fitted to the window;
  - the overview has the use case, a run summary and the run's own narrative summary (taken from its report, exact-timestamp match only, no new LLM call);
  - `--evaluation` adds an optional evaluation page (criteria, scores, reasons, scores across iterations) from the evaluation stored in the run.

Build the C3 demo (from the repo root, `taxonomy` env):

```bash
python benchmark/export_wiki.py examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350.json \
    --corpus examples/c3-git-at-scale/c3-git-at-scale_corpus.json \
    --sources benchmark/c3-git-at-scale/sources.csv \
    --systems benchmark/c3-git-at-scale/passage_systems.csv \
    --system-names benchmark/c3-git-at-scale/systems.csv \
    --design-points examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350_design_points.json \
    --config examples/c3-git-at-scale/c3_git_at_scale_config.yaml --evaluation
open examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350_wiki/html/index.html
```

Still open: the demo dry run (W4), the paper figures (W5), and the optional llmwiki-cli stock site (W6).

### 13.5 Open questions for the branch

- **Value-page links:** do they also link to their passages' sources, so source nodes show which decisions they inform? This makes the graph denser. Decide on the C3 export.
- **Several runs in one site:** out of scope (R8 later). One site per run for now.
- **Design-point verdicts:** once the judge (A13) or the human ratings exist, add the verdict (workable / conditional / unfeasible) to the point pages and color the layer by it.

## 14. References

- Karpathy's LLM-wiki pattern (April 2026): overview at <https://denser.ai/blog/llm-wiki-karpathy-knowledge-base/>; implementations under the GitHub topic <https://github.com/topics/karpathy-llm-wiki>
- QMD: <https://github.com/tobi/qmd>
- llmwiki-cli: <https://github.com/doum1004/llmwiki-cli>
- OpenWiki: <https://github.com/langchain-ai/openwiki>
- OpenKB: <https://github.com/VectifyAI/OpenKB>
- LightRAG: <https://github.com/HKUDS/LightRAG> (`insert_custom_kg`: `docs/ProgramingWithCore.md`)
- Cognee: <https://github.com/topoteretes/cognee>
- rust-llm-wiki: <https://github.com/joshgarnett/rust-llm-wiki>
- Other LLM-wiki implementations: <https://github.com/ddsyasas/llm-wiki>, <https://github.com/nvk/llm-wiki>, <https://github.com/ussumant/llm-wiki-compiler>
- Obsidian CLI: <https://obsidian.md/cli>; guide: <https://www.dsebastien.net/the-complete-guide-to-the-obsidian-cli-everything-you-can-do-from-the-terminal/>
- Kùzu archival (Oct 2025): <https://news.ycombinator.com/item?id=45560036>
- graphify: installed in this repo (`.claude/skills/graphify/`), `graphify --help`
