# Toy design space: Git hosting at scale

A small design space for teaching search and explain: five dimensions (where repository state lives,
replication, reference updates, client data transfer, serving reads), each with three or four values. It is a
hand-curated slice of the C3 case (`benchmark/c3-git-at-scale/`): the dimensions, values and relations are
curated in `spec.yaml`, and every value inherits the passages and stances of the C3 mined values it names, so
the evidence is the pipeline's. The C3 systems (GitHub Spokes, Cursor Continuity, Microsoft VFS for Git and
Scalar, ...) are points of the space; `spec.yaml` lists them.

```bash
python examples/toy-git-hosting/build.py taxonomy        # spec.yaml -> toy-git-hosting_taxonomy_*.json
python examples/toy-git-hosting/build.py workspace --out ~/Documents/GitHub/ddspace-sandboxes/toy-git-hosting
```

The workspace has a wiki without quotes, and the agent guide. `cases/` holds a search brief and a solution to
explain (in the style of GitHub's Spokes), in the format of `study/designing2027/cases/`.

Limits: one C3 source (Cursor's "Git at any scale") discusses every system, so it attests almost any
combination; the per-value passages and stances carry more of the evidence than `attested_by` does.

## Running search and explain on it

Interactively, with Codex in the workspace (from the repository folder, `taxonomy` active):

```bash
TOY=~/Documents/GitHub/ddspace-sandboxes/toy-git-hosting
python examples/toy-git-hosting/build.py workspace --out $TOY
cp examples/toy-git-hosting/cases/2-spokes-explain/problem.md $TOY/PROBLEM.md
cp examples/toy-git-hosting/cases/2-spokes-explain/solution.md $TOY/SOLUTION.md
cd $TOY && ddspace agent setup --skills --yes
```

Then one Codex session per case. `CODEX_HOME` keeps your login while the throw-away `HOME` keeps your personal
skills out, as in the study; the study key lets `ddspace point` write its descriptions:

```bash
export OPENAI_API_KEY=$STUDY_OPENAI_API_KEY
CODEX_HOME=~/.codex HOME=$(mktemp -d) codex exec -m gpt-6-luna -c 'model_reasoning_effort="high"' \
  -s workspace-write -c sandbox_workspace_write.network_access=true --skip-git-repo-check \
  "Use the ddspace-search skill. The problem is in PROBLEM.md. Write ./rationale/hosting-search.json, run ddspace rationale check until it is clean, then run ddspace rationale build rationale/hosting-search.json."
CODEX_HOME=~/.codex HOME=$(mktemp -d) codex exec -m gpt-6-luna -c 'model_reasoning_effort="high"' \
  -s workspace-write -c sandbox_workspace_write.network_access=true --skip-git-repo-check \
  "Use the ddspace-explain skill. The problem is in PROBLEM.md and the solution in SOLUTION.md. Write ./rationale/spokes-explain.json, run ddspace rationale check until it is clean, then run ddspace rationale build rationale/spokes-explain.json."
ddspace wiki open
```

The explainers are in the wiki: `site/explainers/hosting-search.html` and `site/explainers/spokes-explain.html`.
