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
