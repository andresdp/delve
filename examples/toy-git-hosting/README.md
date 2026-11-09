# Toy design space: Git hosting at scale

A small design space for teaching search and explain: five dimensions (where repository state lives,
replication, reference updates, client data transfer, serving reads), each with three or four values. It is a
hand-curated slice of the C3 case (`benchmark/c3-git-at-scale/`): the dimensions, values and relations are
curated in `spec.yaml`, and every value inherits the passages and stances of the C3 mined values it names, so
the evidence is the pipeline's. The C3 systems (GitHub Spokes, Cursor Continuity, Microsoft VFS for Git and
Scalar, ...) are points of the space; `spec.yaml` lists them.

```bash
python examples/toy-git-hosting/build.py taxonomy        # spec.yaml -> toy-git-hosting_taxonomy_*.json
python examples/toy-git-hosting/build.py workspace --out ~/Documents/GitHub/ddspace-sandboxes/toy-git-hosting/M
python examples/toy-git-hosting/build.py no-space --out ~/Documents/GitHub/ddspace-sandboxes/toy-git-hosting/N
```

The workspace has a wiki without quotes, and the agent guide. `cases/` holds a search brief and a solution to
explain (in the style of GitHub's Spokes), in the format of `study/designing2027/cases/`.

Limits: one C3 source (Cursor's "Git at any scale") discusses every system, so it attests almost any
combination; the per-value passages and stances carry more of the evidence than `attested_by` does.

## Running search and explain on it

Two conditions, as in the C1 study: **M**, the toy space as a wiki, and **N**, an empty folder where the agent
works zero-shot (`space: null`). In both, every design point gets a description from `ddspace point` that ends
with the point's own trade-off (`Trade-off: …`), and every step records its trade-offs against the requirements
(`tradeoffs`). In N, `ddspace point --no-space` describes the agent's own `Dimension: Value` names with the same
prompt and the same model as M (`DDSPACE_POINT_MODEL`).

Set up both folders (from the repository folder, `taxonomy` active):

```bash
TOY=~/Documents/GitHub/ddspace-sandboxes/toy-git-hosting
python examples/toy-git-hosting/build.py workspace --out $TOY/M
python examples/toy-git-hosting/build.py no-space --out $TOY/N
(cd $TOY/M && ddspace agent setup --skills --yes)
for c in M N; do
  cp examples/toy-git-hosting/cases/2-spokes-explain/problem.md $TOY/$c/PROBLEM.md
  cp examples/toy-git-hosting/cases/2-spokes-explain/solution.md $TOY/$c/SOLUTION.md
done
```

Then four Codex sessions, search and explain in each folder. `CODEX_HOME` keeps your login while the throw-away
`HOME` keeps your personal skills out, as in the study; the study key lets `ddspace point` write descriptions:

```bash
export OPENAI_API_KEY=$STUDY_OPENAI_API_KEY DDSPACE_POINT_MODEL=openai/gpt-5.6-luna
codex_run() {  # folder, prompt
  (cd "$1" && CODEX_HOME=~/.codex HOME=$(mktemp -d) codex exec -m gpt-6-luna -c 'model_reasoning_effort="high"' \
    -s workspace-write -c sandbox_workspace_write.network_access=true --skip-git-repo-check "$2")
}
SEARCH="Use the ddspace-search skill. The problem is in PROBLEM.md. Write ./rationale/hosting-search.json and run ddspace rationale check until it is clean."
EXPLAIN="Use the ddspace-explain skill. The problem is in PROBLEM.md and the solution in SOLUTION.md. Write ./rationale/spokes-explain.json and run ddspace rationale check until it is clean."
codex_run $TOY/M "$SEARCH Then run ddspace rationale build rationale/hosting-search.json."
codex_run $TOY/M "$EXPLAIN Then run ddspace rationale build rationale/spokes-explain.json."
codex_run $TOY/N "$SEARCH There is no design space here: work zero-shot. Then run ddspace rationale build rationale/hosting-search.json --out ."
codex_run $TOY/N "$EXPLAIN There is no design space here: work zero-shot. Then run ddspace rationale build rationale/spokes-explain.json --out ."
```

The M explainers are in the wiki (`ddspace wiki open`, then `site/explainers/`); the N explainers are next to
the rationale files, in `$TOY/N/explainers/`.

## Recorded runs

`runs/M/` and `runs/N/` hold the rationale files of the second toy run (2026-11-09; `gpt-6-luna`, effort high,
schema `ddspace-rationale/6`, descriptions by `openai/gpt-5.6-luna`), for the paper's figures. `build.py` rebuilds
the same wiki (the M files' `graph_sha256` matches it), so their explainers can be rebuilt:

```bash
(cd $TOY/M && ddspace rationale build ~/Documents/GitHub/delve/examples/toy-git-hosting/runs/M/hosting-search.json)
mkdir -p /tmp/toy-n && (cd /tmp/toy-n && ddspace rationale build ~/Documents/GitHub/delve/examples/toy-git-hosting/runs/N/hosting-search.json --out .)
```
