---
title: "feat: graph-aware retrieval for `ddspace ask` — question-driven expansion, decision areas, graph walk"
type: feat
status: proposed (2026-10-15); plan only, not scheduled
date: 2026-10-15
related: >-
  src/delvedspace/chat.py (TreeDex index and answer), src/taxonomy_generator/wiki/{model,query}.py (graph.json,
  read functions), docs/plans/2026-10-15-refactor-taxonomy-data-layer-plan.md (read operations R3, R8, R10, R18)
---

# Question-driven graph expansion for `ddspace ask`

## Problem

`ddspace ask` retrieves in one step ([chat.py](../../src/delvedspace/chat.py)):

1. TreeDex shows the LLM a tree of page titles and one-line summaries and the LLM picks the relevant pages;
2. the answer prompt writes from those pages only.

The tree is a containment hierarchy: Overview → Dimensions → their Values, and Synthesis → Design points. Choosing
a dimension also brings its value pages, because they come right after it in the index. Nothing follows the
**relations of the design space**:

- **Relations stay text.** A dimension page says "affects the outcomes of State Change Recipients and Effects",
  but links are reduced to plain labels (`_page_text`). The answer sees the related dimension's name, never its
  page. Questions like "if I choose X, what else must I decide?" stop after the first hop.
- **The picker can't see relations.** They are not in the summaries it chooses from, so it can't anticipate them.
- **Sources are not indexed.** `_entries` skips `sources/`, so source-centric questions ("what does s3
  recommend?") cannot reach the source's page.
- **One pick, no follow-up.** Two-hop questions ("the decisions that require X, and their alternatives") cannot be
  answered.

Of GraphRAG's three steps, Delve needs only part. The first step, extracting entities and relations with an LLM,
is unnecessary: Delve already has the graph (`raw/graph.json`: typed relations with reading sentences, evidence
with stances, design points). What `ask` lacks is retrieval that **uses the edges**, plus, for large wikis,
GraphRAG's **community level**: groups of related dimensions with summaries (see "Communities").

## Goal

After the first pick, expand the retrieved set along the graph's edges. **The LLM decides which edges to follow,
driven by the question**, within a fixed budget. A deterministic expansion is the first variant and the baseline.

Non-goals:
- free-form agentic navigation with open-ended tool calls (a possible later `--deep`);
- LLM entity extraction (the graph already exists);
- any change to the design space. The wiki gains only generated area pages, marked as generated.

## Graph available for expansion

From `raw/graph.json` (demo workspace, 2026-10-15): 8 dimensions, 42 values, 17 sources, 32 design points.

| Edge type | Between | Carries | Reading for the LLM |
|---|---|---|---|
| `relation` | dimension → dimension | `relation` (requires, affects, constrains, …), `reading` | the reading sentence, e.g. "X requires Y to be decided first" |
| `has_value` | dimension → value | — | "Y is an alternative (or outcome) of X" |
| `evidence` | source → value | `stance` (accepts, rejects, supports, both) | "source s3 accepts Y" |
| `design` | design point → value | — | "point P004 combines Y with …" |

Every node has a wiki page (`href`), so following an edge means adding the page at its other end. Degrees grow
with the corpus (value → sources reaches about 20 in C1/C2), so each step must show a capped, ranked frontier.

## Variants

| Variant | Who decides what to follow | Extra LLM calls | Role |
|---|---|---|---|
| **V0 `none`** | — (today) | 0 | baseline |
| **V1 `graph`** | a fixed rule: one hop from every picked dimension or value, through relations, then design points, then the top sources by evidence, until a page budget is reached | 0 | deterministic baseline; cheap default candidate |
| **V2 `llm`** | **the LLM, from the question**: it sees the frontier (the edges that leave the retrieved set) and picks the edges to follow; it may take a second hop | 1–2 small calls (titles and edges only, no page text) | question-driven lateral expansion on top of TreeDex |
| **V3 `walk`** | the LLM, walking the graph from its coarsest level (see "Generalization") | 2–5 bounded calls | the general model; needs areas to scale |

### V2 in detail

1. **Initial pick.** TreeDex as today.
2. **Frontier.** From `graph.json`, collect the edges leaving the picked nodes whose far end is not yet retrieved.
   - Each edge is shown as one line: an edge id, its type, its reading sentence or a templated one, the target's
     title, and a short summary (the same one-liners the picker sees).
   - Caps: at most 40 edges in total and 8 per type and node. Rank evidence edges by passage count and design
     points by the number of retrieved values they contain.
3. **Selection (one LLM call, structured output).** The input is the question, the titles of the retrieved pages
   and the frontier. The output is `{follow: [edge_id], reason: str, done: bool}`.
   - The ids are validated against the frontier; unknown ids are dropped.
   - The prompt asks for the edges *needed to answer this question*, and says that following none is a valid
     answer.
4. **Second hop (optional).** If `done` is false and the budget allows, rebuild the frontier from the newly added
   nodes and repeat once. `max_hops` defaults to 2.
5. **Answer.** Expanded pages are appended to the context after the picked ones. Each carries one line of
   provenance, e.g. "Retrieved because: X requires Y to be decided first". This helps the answer explain a chain of
   decisions, and makes it visible why a page is there.
6. **Output.** `--json` gains `expansion: [{hop, edge, reason}]` and the token and call counts. `--why` prints the
   path.

**Budgets** (settings under `chat:` in `ddspace.yaml`):
- `expand: none | graph | llm`;
- `max_hops: 2`;
- `max_pages: 8` added pages;
- `max_context_tokens`, below the model's limit; the lowest-ranked expanded pages are cut first.

### Prerequisites (useful in every variant)

- **P1. Put relations in the picker's summaries.** Each dimension summary gains "requires: …; affects: …" (short).
  The first pick can then anticipate related decisions.
- **P2. Index the source pages** under a new top-level "Sources" node, with a one-line summary (the stored source
  summary when there is one, otherwise the title).
- **P3. Keep link targets in page text.** Write "Name (concepts/slug)" instead of only "Name". The selection step
  and the answer can then refer to pages precisely. This does not change the wiki files, only the index text.

## Communities: decision areas (for large wikis)

GraphRAG adds a level above the entities: communities of related entities, each with an LLM-written summary. Those
summaries let a retriever start broad, and they answer global questions ("what are the main tensions in this
design space?") by map-reduce over the communities. In Delve the matching level sits **above the dimensions**:
groups of related decisions, called **decision areas** here (e.g. "data storage and replication", "deployment and
rollback").

### When it matters

| Case | Dimensions (selected / final) |
|---|---|
| Demo | 8 |
| C2 (10-02 run) | 10 / 14 |
| C1 (10-02 run) | 19 / 20 |
| C3 (loop feedback run, 10-15) | 25 / 25 |
| C3 (exclusivity run, uncapped, 10-15) | 42 / 44 |

Today the picker sees all dimensions as siblings under one folder. Up to about 15 that is fine. At 25–45 a flat list
makes the first pick harder, and global questions need many pages at once. Areas are built **only above a
threshold** (`min_dimensions_for_areas: 15`); smaller wikis keep today's tree.

### How the areas are built

- **Graph:** dimensions are the nodes. Weighted edges come from three signals, all present in `graph.json`:
  - relations (requires, affects, constrains, …): a strong signal, but sparse;
  - **shared sources**: the Jaccard similarity of the sources adopting each dimension's values; the main signal;
  - optional: similarity of the dimensions' descriptions (needs embeddings; off at first).

  Design points are left out: they are a random sample, not evidence of relatedness.
- **Algorithm:** **Leiden** on a **networkx** graph, with a fixed seed. Leiden is GraphRAG's choice: unlike
  Louvain, it guarantees well-connected communities, and its resolution parameter controls the size of the areas.
  - **Graph:** build a weighted `networkx.Graph` from `graph.json`. networkx goes in a new `[graph]` extra, which
    `[chat]` includes.
  - **Leiden implementation**, to settle when building:
    - `leidenalg` with `python-igraph` (C extensions with wheels): convert with `igraph.Graph.from_networkx`, then
      run `leidenalg.find_partition(..., RBConfigurationVertexPartition, weights=..., resolution_parameter=...,
      seed=...)`;
    - or networkx's own Leiden function, if the installed version has one that works without a backend package.
      Check this before adding `leidenalg`.
  - **Fallback:** Louvain (`networkx.community.louvain_communities(G, weight=..., resolution=..., seed=...)`,
    pure Python), when Leiden is not installed. The algorithm actually used is recorded in the area metadata.
  - **Settings:** `wiki.area_algorithm: leiden | louvain`, and `wiki.area_resolution` (default 1.0). The
    resolution is tuned so that the case wikis get 3–8 areas.
  - **Hierarchy:** a second level runs Leiden again inside any area of more than 15 dimensions. This is
    GraphRAG's hierarchical approach, done here with two plain runs, without its heavy `graspologic` dependency.
  - The graph has at most a few dozen nodes, so either algorithm is instant. The output is 3–8 areas of at least
    2 dimensions; leftover dimensions go to "Other decisions".
- **Summaries:** one LLM call per area at `ddspace wiki build`, with the same model and storage pattern as the source
  summaries (`.ddspace/area_summaries.json`, keyed by the member set and the prompt version, so a rebuild with the
  same areas makes no calls).
  - Each summary gives a name, a 2–3 sentence description of what the area decides, and its most contested
    decisions (from the statuses).
  - Like all generated text, it is marked as such and is not evidence.
- **Naming fallback:** without the LLM (`--no-llm`), an area is named after its best-supported dimension.

### How retrieval uses them

1. **Tree level for the picker.** The index becomes Overview → **Areas** → Dimensions → Values. Each area's
   one-line summary helps the first pick narrow down before choosing dimensions.
   - Picking an area must not pull in its whole subtree: in TreeDex's page ranges, a node includes its
     descendants.
   - So the answer context is built from the selected **node ids** (each node's own page), not from TreeDex's
     `result.context`. This is a small change in `ask` that the expansion needs anyway.
2. **Edges for expansion.** The frontier (V2) gains "in the same area as" edges, so the LLM can widen to sibling
   decisions when the question is broad.
3. **Global questions (map-reduce, GraphRAG "global search").**
   - `ask --global`, or automatic when the first pick selects only areas or overview pages: each area summary
     plus its dimension summaries goes through a short "what does this area say about the question?" call.
   - A final call combines the partial answers.
   - Cost: one call per area plus one, so it is opt-in and capped by `max_areas`.

### Wiki and query outputs (also useful to people)

- `synthesis/areas.md` lists the areas with their summaries and dimensions. Each dimension page gets an "Area:"
  line.
- `raw/graph.json` gains `area` nodes (`a:1`) and `in_area` edges. This is a new node kind, so `schema_version`
  goes from 1 to 2, and readers of version 1 must accept or ignore it.
- `ddspace query areas`, and `show a:1`.

## Generalization: from picking in a tree to walking a graph

### What TreeDex actually does (0.1.5)

`TreeDex.query` is one LLM call, not a walk:
- It serializes the **whole tree** (titles and summaries, page text stripped) as JSON into the retrieval prompt.
- The LLM returns `node_ids` and a reasoning string.
- The context is each picked node's page **range**, so a node brings its descendants.

So the **generation** prompt holds only the selected nodes' text. But the **selection** prompt holds the whole
outline, every question, and the LLM picks in one shot: it does not descend level by level.

Measured on the demo index (2026-10-15):

| | Size |
|---|---|
| Nodes in the tree | 92 |
| Selection prompt, outline only (`strip_text_from_tree`, JSON with `indent=2` and page-index fields) | ~33.9k characters, ~8.5k tokens |
| All page text (never sent at once) | ~83k characters, ~21k tokens |

The outline grows with the wiki: 8 dimensions already take 8.5k tokens, and `USAGE.md` reports about 25–30k tokens
per question on the C3 sample. Part of the outline is overhead the LLM does not need (indentation,
`start_index`/`end_index`/`physical_index`). Nothing in it follows anything but containment.

### Library choice: TreeDex, PageIndex, or our own module

| Option | What it gives | What it does not give | Verdict |
|---|---|---|---|
| **Keep TreeDex 0.1.5** | page-range text embedding, one retrieval prompt, a JSON extractor | iterative descent, lateral moves, communities; and the page-range embedding causes the "a node brings its descendants" behavior we want to drop | We already build the index ourselves (`chat.build_index`, deterministic, no LLM), so a "refactor" would mostly delete what we use |
| **Move to PageIndex** (VectifyAI, MIT, `pip install pageindex`) | building a tree from long **PDFs** (from the layout); retrieval described as agentic tree search with LLM reasoning ("reads only the nodes its reasoning reaches"); OpenAI models in its quickstart | a graph: no typed edges, lateral moves or communities; markdown input not mentioned; part of it (OCR, storage, MCP) is in a hosted Cloud | Its main value, tree construction from PDFs, is something Delve does not need. The walk's lateral half and the areas would still be ours |
| **Own module `graphwalk.py`** (recommended) | both modes over `graph.json` and the wiki pages: **one-shot** (today's behavior, kept as the V0 baseline, with a lean outline) and **walk** (V3) | — | Fits the data we have; removes `treedex` and its PyMuPDF import from `[chat]` once the evaluation confirms V3; about the size of `chat.py` today |

**Before building, read PageIndex's search code.** If it accepts a tree we provide and exposes its search steps, it
could run the vertical part of the walk (down and up moves), and we would add the lateral moves on top. The
repository page (checked 2026-10-15) does not say whether its search is iterative or a single selection, so this
is unverified. Source: https://github.com/VectifyAI/PageIndex.

### The generalized model: a vectorless graph walk

Keep TreeDex's core idea, *the LLM navigates by titles and summaries, no embeddings*, but over a **graph with
levels** and over several steps:

- **Levels** (the spine, from the communities):
  - L0 overview;
  - L1 decision areas (and sub-areas when a second level exists);
  - L2 dimensions;
  - L3 values;
  - leaves: sources and design points.
- **Moves from an open node:**
  - **down**: open its children (area → dimensions, dimension → values, value → its sources);
  - **up**: open its area;
  - **across**: follow a typed edge (relation with its reading, same area, evidence with stance, design point);
  - **jump**: a keyword search (`query.search`), to recover when the walk started in the wrong place.
- **A step:** the LLM sees the question, the currently open nodes (title and summary), and the moves available
  from them, each in one line with an id (as in V2's frontier). It returns `{open: [move ids], keep: [node ids],
  done, reason}`:
  - nodes not kept are dropped from the view, which bounds the next prompt;
  - `keep` also marks what goes into the answer context.
- **Start view.** The coarsest level that fits a token budget:
  - large wikis start at the **areas**, with summaries and inter-area edges (the number of relations between two
    areas);
  - small wikis without areas start at the **dimensions**, which is equivalent to today's first pick, without the
    page-range side effect.
- **Budgets:** `max_steps` (default 3), beam width (open nodes per step, about 12), and the maximum context pages.
- **Answer:** from the kept nodes' own pages, each with its provenance path (how the walk reached it).

### How the variants relate

| Variant | Entry | Walk policy | Calls |
|---|---|---|---|
| V0 | TreeDex pick | none | 2 |
| V1 | TreeDex pick | fixed one-hop rule | 2 |
| V2 | TreeDex pick | LLM chooses lateral edges for 1–2 hops | 3–4 |
| **V3 `walk`** | coarsest level within the budget (areas, or dimensions) | LLM chooses down, up, across and jump moves for up to `max_steps` | 2–5, each with a **bounded** prompt |

V1 and V2 keep TreeDex and add the graph. **V3 replaces TreeDex's one-shot pick with the walk**, and the areas
are what make it scale: a 42-dimension wiki starts from about 6 area summaries instead of a 400-node tree.

### Trade-offs

| For V3 | Against V3 |
|---|---|
| The prompt per step is bounded, whatever the wiki's size; expected to cost fewer tokens than TreeDex on large wikis (to be measured) | More sequential calls, so more latency |
| Multi-hop and lateral moves are native | No global view at once: a wrong first step can miss the answer (mitigations: start from the coarsest full view; the jump move; the keep set can hold several branches) |
| The path is explainable (provenance per page) | Walk variance between runs (two runs per question in the evaluation) |
| Removes the TreeDex 0.1.5 page-range contract and its PyMuPDF import | Our own code to maintain instead of a library |

### Prior work to cite or compare (to check before the write-up)

| Approach | Idea | Corresponding piece here |
|---|---|---|
| GraphRAG | communities, summaries, global search | areas |
| RAPTOR | a tree of recursive summaries | the levels |
| Think-on-Graph | LLM beam search over a knowledge graph | the walk |

Delve's twist is that the graph is not extracted for retrieval: it is the mined design space, with typed decision
relations and stance-labelled evidence.

## Evaluation

The variants are compared before any default changes.

- **Question set.** About 10 questions per case (demo, C1, C2, C3), written to need the graph:
  - one-hop relations ("what must be decided before X?");
  - two hops ("for decisions that X affects, which alternatives are contested?");
  - source-centric questions ("which alternatives does source s3 accept?");
  - design points ("which sampled points combine X and Y?");
  - control questions that need no expansion, to catch over-expansion;
  - **global questions** ("what are the main tensions in this design space?"), mainly for the large wikis (C1, C3
    with 42 dimensions).

  Each question records its **gold pages** (the pages an answer must use) and **gold facts** (short claims).
- **Metrics:**
  - **page recall**: gold pages retrieved;
  - **context precision**: retrieved pages that are gold;
  - **fact recall** in the answer, judged by an independent model (`gpt-5.4-mini`, not the generator);
  - **citation validity**: cited passage ids that are in the context and support the claim;
  - LLM calls and tokens per question.
- **Runs.** V0, V1, V2 and V3 on the same questions, each with and without areas on the wikis above the threshold.
  V2 and V3 are run twice to see how much their LLM choices vary. Tokens per question are compared between V3 and
  TreeDex as the wiki grows (demo → C2 → C1 → C3 with 42 dimensions).
- **Area quality,** apart from `ask`:
  - modularity of the partition;
  - stability: the same areas with another seed, and after a rebuild with one source added;
  - a human check that each area reads as one theme (about 5 minutes per case).
- **Success criteria:**
  - V2 beats V1 on page and fact recall for the relational questions;
  - V2 is no worse on the control questions;
  - V2 costs at most 2 extra small calls per question.

  If V1 comes close to V2, V1 becomes the default (no extra calls) and V2 stays opt-in.
- **Areas are worth it** if they raise first-pick page recall on the large wikis, or global-question fact recall,
  without hurting the small ones. Small wikis are unaffected by construction (the threshold).

## Change impact

| Area | Change | Risk |
|---|---|---|
| `src/delvedspace/chat.py` | `_entries`: P1 (relation summaries) and P2 (a Sources node); `_page_text`: P3 (keep link targets); a new `expand(graph, picked, question, llm, settings)` with frontier, selection and hops; `ask` calls it between the pick and the answer; `Answer` gains `expansion` | Medium. The TreeDex page order is a contract (depth first); P2 adds a top-level node at the end of the order, after Synthesis |
| `taxonomy_generator/wiki/query.py` | A `neighbors(graph, node_id, types, limit)` read function, reused by the frontier and later by `ddspace query` | Low (additive) |
| Selection prompt | New, versioned (`EXPANSION_PROMPT_VERSION`), with injection rules: the frontier holds generated labels and readings, no quoted passages | Low |
| `src/delvedspace/cli.py` (`ask`) | `--expand none\|graph\|llm` overrides the setting; `--why` shows the path | Low |
| Workspace settings (`ddspace.yaml` template, `workspace.Settings`) | A `chat:` section (`expand`, `max_hops`, `max_pages`, `max_context_tokens`) | Low. Defaults keep today's behavior until the evaluation decides |
| Chat index | Rebuilt by `ddspace wiki build` (no LLM) | Low. `ddspace check` already flags a stale index |
| Tests | Unit tests with a fake LLM: frontier construction and caps; validation of selected ids (unknown and duplicate); hop limit and `done`; budget cuts; provenance lines; V1 determinism; `--json` fields; P1–P3 index changes. The existing chat tests must still pass | — |
| Evaluation assets | `benchmark/ask_eval/` with the question sets (they contain no source text), a runner and a report | Low |
| Docs | `USAGE.md` (`ask --expand`, settings); the `AGENTS.md` guide (unchanged: agents navigate with `ddspace query` themselves); `CONCEPTS.md` ("graph expansion") | — |
| Cost | V2: +1–2 calls per question, each with a short prompt (frontier only, about 2–4k tokens); the answer context grows by at most `max_pages` pages | Bounded by the settings |

| Areas: `wiki/model.py`, `delvedspace/wiki_build.py` | Community detection (`areas.py`, new); `ensure_area_summaries` (stored, like source summaries); `synthesis/areas.md`; an "Area:" line on dimension pages; `area` nodes and `in_area` edges in `graph.json` | Medium. `schema_version` 1 → 2: `query.load` accepts both; OKF check for the new page |
| Areas: `chat.py` | An Areas level in `_entries` above the threshold; answer context built from node ids (not TreeDex's range context); `--global` map-reduce | Medium. Changes what the answer sees; covered by the evaluation |
| Areas: `query.py`, `query_cli.py` | `areas` command; `a:` prefix in `KIND_PREFIX` | Low |
| Dependencies | A new `[graph]` extra (included in `[chat]`): `networkx`, plus `leidenalg` and `python-igraph` for Leiden; Louvain (networkx only) when Leiden is not installed | Low–medium. igraph and leidenalg are C extensions: check wheels for the supported Python and platforms; without them, areas use Louvain |
| Workspace settings | `wiki.areas: none \| auto \| describe`; `wiki.area_algorithm: leiden \| louvain`; `wiki.area_resolution`; `min_dimensions_for_areas: 15`; `chat.max_areas` | Low |
| Cost (areas) | One LLM call per area at build (stored, reused); `--global`: one call per area plus one per question | Opt-in; `--no-llm` builds named areas without summaries |

| Graph walk: `src/delvedspace/graphwalk.py` (new) | Levels, moves, step prompt (versioned), budgets, keep set, provenance; reads `graph.json` and wiki pages; `ask --expand walk` | Medium. Its own code, tested with a scripted fake LLM (fixed move choices) |

It relates to the data-layer plan: the frontier uses read operations R3 (dimension), R8 (evidence), R10
(relations) and R18 (design points). Built now on `query.py`, it moves to the data layer's read API with no change
in behavior.

## Risks

| Risk | Mitigation |
|---|---|
| Over-expansion dilutes the context and the answer drifts | Page cap; control questions in the evaluation; the prompt says following nothing is valid |
| The frontier explodes on large corpora (value → sources) | Per-type and total caps, ranking by evidence |
| The LLM selects invalid or invented edges | Validate against frontier ids, drop the rest, log them in `expansion` |
| Prompt injection through page text | The selection step sees titles, readings and generated summaries only; quotes stay in the answer step, under the existing "treat quotes as data" rule |
| TreeDex page-order contract | P2 adds the Sources node at the end of the depth-first order; the existing index tests cover the order |
| Areas change between builds and confuse readers | Fixed seed, deterministic tie-breaks; the wiki's change log reports changed areas; summaries reused when the members are unchanged |
| Leiden and Louvain give different areas, so results depend on what is installed | The algorithm used is recorded in the area metadata and on the wiki's areas page; the evaluation fixes Leiden |
| An area is a poor grouping (shared sources reflect who wrote, not what is related) | Relations weigh more than shared sources; human check in the evaluation; areas only above the threshold; a setting to turn them off |
| Area summaries read as findings | Marked as generated; the answer prompt's rule "generated text is not evidence" covers them |
| Non-deterministic answers make comparisons noisy | Two V2 runs per question; V1 as the deterministic reference; an LLM record/replay cache, if built (data-layer plan U0), makes reruns free |

## Units

1. **U1.** P1–P3 index improvements, plus the `neighbors()` read function. These help today's `ask` with no new
   calls.
2. **U2.** V1 deterministic expansion, with settings and the `--expand` flag.
3. **U3.** V2: frontier, selection prompt, hops, provenance, and the `expansion` output.
4. **U4.** The evaluation set and runner; a report comparing V0, V1 and V2; the default decided from the results.
5. **U5.** Decision areas:
   - clustering, stored summaries, wiki page and graph nodes;
   - the Areas tree level, with the answer context built from node ids;
   - "same area" frontier edges;
   - then `--global` map-reduce.

   Evaluated with U4's sets on C1 and C3. U5 can start after U1; it does not need V2.
6. **U6.** V3 graph walk on the area spine, in our own `graphwalk.py`, with the one-shot mode as V0
   (see "Library choice"); first, a short read of PageIndex's search code. It reuses V2's frontier lines and U5's areas. If it matches or beats
   V2 at lower cost on the large wikis, it becomes the default there, and TreeDex stays for small wikis or is
   retired.

## Open questions

1. Should V2's selection step also be able to *drop* initially picked pages it finds irrelevant, or only add?
2. Should provenance lines appear in the human answer, or only in `--why` and `--json`?
3. Should the evaluation's question sets be part of the paper's artifact, or stay internal?
4. Areas: should the grouping also be offered to the mining pipeline (e.g. to the selection step, or as a report
   section), or stay a wiki and retrieval aid?
5. Areas: is a fixed partition enough, or should a dimension be allowed in two areas (overlapping communities)?
6. Walk: should the `[chat]` extra keep TreeDex once V3 exists, or should V3 (with its start view at the
   dimensions) replace it for all sizes?
