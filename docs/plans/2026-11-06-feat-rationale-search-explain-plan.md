---
title: "feat: design rationale from a design space: search and explain skills, rationale file, explainer page"
type: feat
status: proposed (2026-11-06)
date: 2026-11-06
related: >-
  docs/plans/improvements.md (row 7), docs/paper/designing2027/DESIGNING2027_PAPER_PLAN.md (local),
  src/delvedspace/{agent,point,query_cli}.py, src/taxonomy_generator/wiki/, study/cain2027/run_sessions.py
---

# Design rationale from a design space: search and explain

## Goal

A coding agent uses a design space to produce **design rationale** as an artifact. There are two directions:

- **Search** (forward). Input: a system context and its requirements. The agent navigates the space, builds
  design points and ends with a small set of **alternatives**. Each choice in each alternative is explained by
  the space (dimension, value, evidence, relations) and by the requirements that drive it.
- **Explain** (reverse). Input: the same kind of context plus an **already defined solution**. The agent breaks
  the solution down into decisions, maps each one onto the space, and explains it. It also shows what else the
  space offered for each decision, and which of the solution's decisions the space does not cover.

Both write the same **rationale file**. `ddspace` checks it and renders an **explainer**: a browsable HTML page
that shows the rationale (and, for search, the alternatives) as a subgraph of the space, with links into the
full wiki for details.

The space is not judged. It may be mined (DelveDSpace) or written by an expert (`ddspace import --kind
decision-model`); the skills and the explainer work the same on both. The same skills also run **without a
space** (condition N), so the rationale with and without a space can be compared.

## What exists

| Piece | Where | Used for |
|---|---|---|
| `ddspace query` (`info`, `dimensions`, `values`, `show`, `search`, `relations`, `evidence`) | `src/delvedspace/query_cli.py`, `src/taxonomy_generator/wiki/query.py` | Navigation |
| `ddspace point` (one value per dimension: description, relation checks, `attested_by` sources and systems) | `src/delvedspace/point.py` | Building and checking design points |
| Agent guide and permissions (`ddspace agent setup`: `AGENTS.md`, CLAUDE.md pointer, allow rules) | `src/delvedspace/agent.py` | Installing the skills |
| Wiki (`raw/graph.json`, HTML pages per dimension, value and source; graph view with the radial layout) | `src/taxonomy_generator/wiki/` | The explainer's data, layout code and link targets |
| Session runner with prompt and model guards, recorded sessions (Codex CLI) | `study/cain2027/run_sessions.py` | Running the study |

New: the two skills, the rationale file and its checker, and the explainer page.

## Key technical decisions

- **KTD1. One rationale file for both directions.** Search and explain differ in how the file is filled, not in
  its shape. Explain is a single alternative (the given solution) plus quotes from the solution and the
  `uncovered` list.
- **KTD2. The file refers to the space by id.** Choices name `dimension_id` and `value_id` from `raw/graph.json`,
  and the file records the graph's hash. The checker rejects unknown ids; the explainer reads labels,
  descriptions and evidence from the graph, so the file stays small and cannot misquote the space.
- **KTD3. Without a space, the same file with free decisions.** `space: null`; choices name the agent's own
  `decision` and `option` labels instead of ids. The checker checks the structure only. The explainer draws
  the agent's own decisions as a small graph, so the N condition gets a comparable explainer.
- **KTD4. "Not chosen" is not "rejected".** In explain, the other values of a mapped dimension are shown as
  **options the space offers**. They are not presented as options the designers considered, unless the
  solution says so. In search, the agent lists the values it considered and set aside, with a reason.
- **KTD5. The explainer lives in the wiki.** The pages go to `wiki/html/explainers/<id>.html` and reuse the
  wiki's assets (d3, CSS, theme), so links to dimension, value and source pages are relative and work offline.
  The rationale files are kept in `<workspace>/rationale/`. `ddspace wiki build` re-renders every explainer, so
  explainers follow the wiki when the space changes; a file whose graph hash no longer matches is flagged as
  stale. The wiki index gets an "Explainers" list.
- **KTD6. Skills, not new agent code.** Search and explain are instructions (skill files) over the existing
  commands, plus `ddspace rationale check` as the agent's feedback loop. `ddspace agent setup --skills` installs
  them for Claude Code (`.claude/skills/`) and Codex (`.agents/skills/`). No LLM call is added to `ddspace`
  except the existing one in `point`.

## The rationale file (`ddspace-rationale/1`)

```json
{
  "schema": "ddspace-rationale/1",
  "id": "fraud-detection-search",
  "mode": "search",
  "space": {"workspace": "c1-mined", "run": "20261016_233651", "graph_sha256": "..."},
  "problem": {
    "title": "Real-time fraud detection for card payments",
    "context": "...",
    "requirements": [
      {"id": "R1", "kind": "functional", "text": "..."},
      {"id": "Q1", "kind": "quality", "attribute": "latency", "text": "p99 < 50 ms per transaction"},
      {"id": "C1", "kind": "constraint", "text": "..."}
    ]
  },
  "alternatives": [
    {
      "id": "A1", "name": "Streaming scoring with a feature store", "summary": "...",
      "choices": [
        {"dimension_id": "12", "value_id": "12.3", "drivers": ["Q1"], "reason": "...",
         "evidence": [{"doc": "s07_p03", "stance": "accepts"}],
         "solution_quote": null}
      ],
      "considered": [{"dimension_id": "12", "value_id": "12.1", "reason": "batch scoring misses Q1", "drivers": ["Q1"]}],
      "open": [{"dimension_id": "20", "reason": "no requirement decides it"}],
      "relations": [{"source": "12", "target": "7", "type": "constrains", "holds": true, "note": "..."}],
      "point": {"description": "...", "attested_by": ["..."]}
    }
  ],
  "comparison": [{"dimension_id": "12", "note": "A1 streams, A2 scores in batch"}],
  "uncovered": []
}
```

In **explain** mode, `alternatives` has one entry (`"id": "S"`, the given solution). Each choice carries
`solution_quote`, the passage of the solution that makes the decision. `considered` is empty unless the solution
names an option it set aside. `uncovered` lists the solution's decisions that match no dimension:
`{"decision": "...", "solution_quote": "...", "nearest_dimension_id": "..." | null}`.

**Without a space**: `space` is `null`, and choices use `{"decision": "...", "option": "..."}` instead of ids.

## Commands

| Command | What |
|---|---|
| `ddspace rationale check FILE` | Validates the schema. With a space, it also checks that ids exist, each value belongs to its dimension, at most one value per dimension in an alternative, drivers name requirements, evidence docs exist, and relation claims match `raw/graph.json`. It prints the problems, one per line, and exits non-zero. The agent runs it until the file is clean. |
| `ddspace rationale build FILE` | Checks, copies the file to `<workspace>/rationale/` and renders `wiki/html/explainers/<id>.html`. Prints the page's path. |
| `ddspace rationale list` | Lists the explainers with mode, alternatives and whether each is stale. |
| `ddspace agent setup --skills` | Also writes the two skills. |

These sit in the shared schema in the usual way: nothing here needs a pipeline (`config.yaml`) setting. The
pipeline side gets a `benchmark/export_wiki.py --rationale DIR` option so the approach's wiki export can render
explainers too (see `improvements.md`, Scope).

## The explainer page

One page per rationale file, built from a template (`explainer.html.j2`) next to `graph.html.j2`:

- **Header:** the problem title, the context (collapsible), the requirements as chips (`R1`, `Q1`, ...).
- **Alternatives bar** (search): one tab per alternative plus "Compare". Explain shows "Solution".
- **Subgraph (centre):** the domain node; the dimensions the rationale touches; for each, the chosen value
  (coloured by alternative) and the other values (greyed: considered in search, offered by the space in explain);
  requirement nodes linked to the choices they drive; relations between the touched dimensions. Radial layout,
  reusing the wiki's code: `radialTargets` and the label orientation move to a shared `assets/graph-layout.js`.
  Untouched dimensions are hidden, with a count ("+18 dimensions not involved").
- **Details panel (right):** for the selected node, the reason, drivers, evidence passages (from the graph),
  relation checks, and for explain the solution quote. Every dimension, value and source links to its wiki page.
- **Compare view** (search): a table with dimensions as rows and alternatives as columns, the differing rows
  first, then the `comparison` notes.
- **Uncovered** (explain): a list of the solution's decisions the space has no dimension for, each with its
  quote and nearest dimension.
- **Without a space:** the same page, with the agent's own decisions as the dimensions and no wiki links.

The page is self-contained (inlined JSON, like `graph.html`) and follows the wiki's theme and phone layout.

## The skills

Both skills tell the agent to cite only what `ddspace` returns, to run `ddspace rationale check` until clean, and
to finish with `ddspace rationale build`.

**`ddspace-search`**

1. Read the problem; give each requirement an id (functional `R`, quality `Q`, constraint `C`).
2. Find the relevant dimensions (`query dimensions`, `query search` per requirement).
3. For each, read the values and their evidence (`query values`, `query evidence`); note which requirements
   favour or rule out each value.
4. Check the relations between the chosen dimensions (`query relations`).
5. Build 2–4 alternatives that differ on the decisions the requirements leave open or in tension. Run
   `ddspace point` on each, and record its description and `attested_by`.
6. Write the file; mark undecided dimensions `open`; write the `comparison` notes.

**`ddspace-explain`**

1. Read the problem and the solution; split the solution into decisions, each with its quote.
2. Map each decision to a dimension and value (`query search`, `query show`); otherwise add it to `uncovered`.
3. Find the drivers among the requirements; say when a decision has none.
4. Check the relations between the mapped decisions; report the ones that do not hold.
5. Run `ddspace point` on the solution's values to see which sources or systems attest the combination.
6. Write the file.

**Without a space** (condition N): the same steps with no `ddspace` commands. The agent names its own decisions
and options, and writes `space: null`.

## Implementation units

| Unit | What | Files |
|---|---|---|
| R1 | Rationale schema (dataclasses or JSON Schema), loader, checker; `ddspace rationale check` | `src/delvedspace/rationale.py`, `cli.py` |
| R2 | Explainer template and renderer; shared `assets/graph-layout.js` (radial layout taken out of `graph.html.j2`); `ddspace rationale build/list`; `wiki build` re-renders explainers and lists them in the index | `src/taxonomy_generator/wiki/{render.py,templates/explainer.html.j2,assets/graph-layout.js}`, `src/delvedspace/{rationale,wiki_build}.py` |
| R3 | The two skills (with and without a space); `ddspace agent setup --skills` | `src/delvedspace/templates/skills/`, `agent.py` |
| R4 | Tests: checker on good and bad files; explainer from the toy space and without a space; headless-browser test of the page (as `test_wiki_graph_browser.py`); `wiki build` keeps explainers and flags stale ones | `tests/unit_tests/` |
| R5 | USAGE.md and SETTINGS.md entries; `benchmark/export_wiki.py --rationale` | docs, `benchmark/` |

Estimate: R1 half a day, R2 one to one and a half days, R3 half a day, R4–R5 half a day: about 3 days.

## Deferred to implementation

- Codex CLI's skill location and format (`.agents/skills/<name>/SKILL.md` is assumed); check against the
  installed Codex version and fall back to an `AGENTS.md` section.
- Whether `point` needs a variant that accepts a partial point (open dimensions) without an LLM description.
- How long solutions are quoted: a quote limit, or offsets into the input file.

## Scope boundaries

- No scoring of alternatives, and no claim that an alternative is best.
- No judging of the space; `uncovered` reports reach, not quality.
- Forces and trade-offs (improvement 2) are not required. When 2a lands, choices can cite forces too.
