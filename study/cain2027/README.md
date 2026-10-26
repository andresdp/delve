# Coding agents designing with a design space (C1 study)

A coding agent (Codex CLI) sketches designs for ML-enabled systems from short briefs, in three conditions:

| Condition | The agent gets |
|---|---|
| N | Nothing but the brief: its own knowledge |
| M | The C1 design space mined by ddspace (seed 42), as a workspace with a wiki, `ddspace query`, `ddspace point` and `AGENTS.md` |
| E | The C1 expert decision model imported as a design space (forces and impacts held out for scoring) |

## Inputs (`inputs/`)

Tracked, with SHA-256 hashes in `inputs/manifest.json`:

- `c1-ml-workflow-full-s42_taxonomy_*.json`: the mined design space, trimmed to what the wiki and queries read
  (selected clusters, last iteration, metrics, critic scores); the pipeline history is dropped (2.8 MB to 0.4 MB).
- `config.yaml`: the run's configuration (no absolute paths).
- `sources.csv`: the source list of the expert study (titles and public URLs).
- `gt_model.json`: the expert decision model (decisions, options, links, forces, impacts).

No source text is included: the M workspace has passage ids but no quotes.

## Building the workspaces

```bash
python study/cain2027/build_workspaces.py build --out <folder>
```

The build refuses inputs whose hashes differ from the manifest, and copies the manifest into each workspace as
`study-manifest.json`. Run sessions from a folder outside this repository, so agents cannot read it.

## Running and scoring

Step-by-step instructions, from the briefs to the committed results, are in `RUNNING.md`; the validation
criteria are in `VALIDATION.md`.

```bash
python study/cain2027/reference.py                    # per-brief expert reference (layer 1) -> references/
STUDY_OPENAI_API_KEY=... python study/cain2027/run_sessions.py --workspaces <folder> --scratch <folder> \
    --model <codex model> [--briefs fraud] [--conditions N,M,E] [--reps 2]
python study/cain2027/score.py --workspaces <folder> [--export-labels]
python study/cain2027/rating.py packets --workspaces <folder>   # blind rating kit (layer 3)
python study/cain2027/rating.py agreement [--unblind]
```

- `briefs.yaml`: the design briefs; `forces` are expert force ids (never shown to the agent).
- `prompt.md` and `design.schema.json`: the same prompt and output schema in every condition. The agent returns
  one concise Architecture Decision Record (ADR) per decision, in the MADR shape: context, drivers, options with
  pros and cons, chosen option and rationale, consequences, and citations.
- `results/summaries/`, `results/designs/`: one sanitized summary and one design (JSON) per session; raw logs
  are not kept. `results/adrs/<session>/`: the same design rendered as Markdown ADRs, with an index, for
  reading and comparing sessions of one brief. `results/scores.json`: per-session metrics (including driver
  recall: the share of the brief's hidden forces that the ADRs' drivers name) and per-condition means and ranges.
- Scoring uses the project's ground-truth matcher with its frozen settings: judge `openai/gpt-5.4-mini`, the
  default distance thresholds and candidate cap, and a verdict cache in `results/judge_cache.json`. The session
  model must differ from the judge. Costs use `rates.yaml` (list prices on a stated date).
