# Reproducing the study

A coding agent (Codex CLI) writes architecture decision records (ADRs) for four ML-enabled systems, each described
in a short brief, under three conditions: **N** (the brief only), **M** (the design space ddspace mined from the
C1 sources) and **E** (the C1 expert decision model, imported as a design space). 4 briefs × 3 conditions × 5
repetitions = 60 sessions. This guide covers five levels, from reading the recorded results to rerunning the
agent:

| Level | What you get | Needs | Time |
|---|---|---|---|
| 1. Read | The two design spaces, every ADR, every score | A browser | - |
| 2. Recompute | Every number in the paper, from the recorded results | Python | 1 minute |
| 3. Inspect the agent's workspaces | The exact N, M and E folders the agent worked in | Python | 2 minutes |
| 4. Rescore | The scores, recomputed from the recorded designs | An OpenAI API key (embeddings only) | 10 minutes, a few cents |
| 5. Rerun | New sessions with the agent, scored | Codex CLI, an OpenAI account | about 1 hour, under $1 |

Commands run from the repository's root folder unless stated otherwise.

## What is where

| Path (in `study/cain2027/`) | Content |
|---|---|
| `briefs.yaml` | The four briefs. `text` is what the agent reads; `forces` are expert force ids, used for scoring only |
| `prompt.md`, `design.schema.json` | The prompt and the output schema, the same in every condition |
| `inputs/` | The mined design space, its configuration, the source list and the expert model, with SHA-256 hashes in `manifest.json` |
| `wikis/c1-mined/`, `wikis/c1-expert/` | The design spaces of M and E as wikis: Markdown (`wiki/`) and HTML (`site/index.html`) |
| `references/` | For each brief, the expert decisions that matter for its forces, with options ranked (written before any session) |
| `results/` | The primary run (MADR titles), one file per session in each subfolder (below) |
| `results-question-titles/` | The same 60 sessions with an earlier prompt wording, a robustness check |
| `run_sessions.py`, `score.py`, `analyze.py` | Run the agent; score its designs; recompute the reported numbers |
| `build_workspaces.py`, `reference.py`, `design.py` | Build the N, M and E workspaces; write `references/`; shared helpers |
| `FINDINGS.md`, `VALIDATION.md` | What the results support and what they do not; how each measure is defined and validated |

Each results folder holds:

- `designs/<brief>-<condition>-r<repetition>.json`: the agent's answer (the ADRs, as JSON);
- `adrs/<session>/`: the same ADRs as Markdown, with an index. Compare the three conditions of one brief side by
  side, for example `adrs/fraud-N-r3/`, `adrs/fraud-M-r3/` and `adrs/fraud-E-r3/` (the paper's example);
- `summaries/<session>.json`: what the agent did: the commands it ran (the `ddspace` calls in full, others as
  counts), the design points it checked, tokens, duration, and fingerprints of the prompt and schema. The raw
  Codex logs are not kept;
- `scores.json`: the metrics per session and per condition;
- `labels/<session>.csv`: each option the agent considered and the expert option the matcher paired it with.
  The `*.checked.csv` copies (N and M of the primary run) hold an author's hand check of each pair, from which
  the matcher's precision is computed;
- `judge_cache.json`: every verdict of the judge model, so that rescoring gives the same matches.

## 1. Read

The two design spaces open in a browser:

- **M**, mined by ddspace: `study/cain2027/wikis/c1-mined/site/index.html` (32 dimensions, 279 values, linked to
  passage ids; the source texts are not included);
- **E**, the expert model: `study/cain2027/wikis/c1-expert/site/index.html` (28 dimensions, 124 values, 40
  relations).

The graph and tree views need the files on disk (download the repository); the anonymous viewer blocks scripts.
The agent itself did not browse these pages: it read the same content through `ddspace query` and `ddspace point`
(level 3).

## 2. Recompute the reported numbers

Install once (Python 3.10 or newer):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Then:

```bash
python study/cain2027/analyze.py
```

This reads `results/scores.json` and the hand-checked labels, without any API call, and prints:

- the results table: the mean, standard deviation and Mann-Whitney p-values per condition. The relevant-decision
  coverage is 0.16 for N, 0.22 for M and 0.30 for E;
- relevant-decision coverage per brief;
- the N vs M comparison: one-sided, and paired by brief and repetition;
- the matcher's precision: 155 of 244 hand-checked pairs correct, 0.64.

For the robustness check, add `--results results-question-titles`.

## 3. Inspect the agent's workspaces

```bash
python study/cain2027/build_workspaces.py build --out ../cain2027-sandbox/workspaces
```

This rebuilds the three folders the agent worked in, outside the repository (the agent must not see the expert
model or the scoring code). It refuses inputs whose hashes differ from `inputs/manifest.json`. No API key is
needed.

- `N/`: empty, apart from the brief added to each session's copy;
- `M/` and `E/`: a ddspace workspace with the wiki and the agent's guide, `AGENTS.md`.

Try what the agent did, from inside `M/` or `E/`:

```bash
cd ../cain2027-sandbox/workspaces/M
ddspace query dims --table
ddspace query values "<a dimension name from the table>" --table
cat AGENTS.md
```

`AGENTS.md` now has one more rule than in the recorded sessions: read the space through the commands, not by
opening `raw/graph.json` (Rule 6, added after the runs; see `FINDINGS.md`).

## 4. Rescore the recorded designs

Scoring matches each option the agent considered to the expert options. Embeddings propose candidate pairs, and
the judge model (`gpt-5.4-mini`) decides each pair. Every recorded verdict is in `judge_cache.json`, so rescoring
the recorded designs makes no judge calls. It needs an OpenAI API key for the embeddings only.

Score a copy, to keep the recorded scores for comparison:

```bash
export OPENAI_API_KEY=sk-...
cp -r study/cain2027/results study/cain2027/results-rescore
python study/cain2027/score.py --workspaces ../cain2027-sandbox/workspaces --results results-rescore
python study/cain2027/analyze.py --results results-rescore
```

The scorer prints one line per session and writes `results-rescore/scores.json`. `--workspaces` is the folder
from level 3; it is used for the grounding and citation measures of M and E.

## 5. Rerun the agent

### What you need

- **Codex CLI**: the recorded sessions used version 0.163.0. Install it and run `codex login`.
- **A Codex model**: the recorded sessions used `gpt-6-luna`. The judge model, `gpt-5.4-mini`, cannot be the
  agent: the runner refuses it.
- **A study API key**: an OpenAI key with a low spending limit. Only the `ddspace` commands inside the M and E
  sessions use it; the agent's model calls go through your Codex login.
- **The workspaces** from level 3.

### Run

Write the new sessions to their own results folder. The recorded ones stay untouched:

```bash
export STUDY_OPENAI_API_KEY=sk-...
python study/cain2027/run_sessions.py --workspaces ../cain2027-sandbox/workspaces \
    --scratch ../cain2027-sandbox/scratch --model gpt-6-luna --reps 5 --results results-rerun
```

For a first check, add `--briefs fraud --reps 1`: three sessions, a few minutes.

Each session runs `codex exec` in a fresh copy of its workspace, with:

- the brief as `BRIEF.md`;
- a private Codex home that holds only your login;
- an allow-listed environment;
- web search turned off.

Only `ddspace` may reach the network, in M and E. The runner prints one line per session, ending in `ok`. A
session takes about 25 seconds in N and 1 minute in M and E. Stop it with Ctrl+C at any time; the same command
resumes, skipping finished sessions.

Then score and recompute, as in level 4:

```bash
export OPENAI_API_KEY=sk-...
python study/cain2027/score.py --workspaces ../cain2027-sandbox/workspaces --results results-rerun
python study/cain2027/analyze.py --results results-rerun
```

The scorer starts from a copy of `results/judge_cache.json`, so pairs judged before keep their verdicts; new
pairs are judged and added.

### What to expect

The agent's model is not deterministic, so a rerun gives other ADRs and other numbers. Compare the conditions:

- the order of relevant-decision coverage, N < M < E;
- E's lead over M;
- M's grounding: almost every choice cites the design space, and the cited passages support the chosen value.

The N vs M difference is the smallest effect (p = 0.055 two-sided in the recorded run). Expect it to vary more
than the others.

### Notes

- **Prompt and model guards.** Every summary records the prompt's SHA-256 and the model. The runner refuses to
  add sessions to a results folder made with another prompt or model, so one folder never mixes setups.
- **User-level skills.** Codex also loads skills from your home folder (`~/.agents/skills`). The private Codex home
  does not hide them. In the recorded sessions, the agent could see five installed skills and opened none (see
  `FINDINGS.md`). To rule them out, move that folder aside while the sessions run.
- **Apple silicon.** If your Python runs under Rosetta, the runner starts Codex as a native program; no action
  is needed.
- **Debugging.** `--keep-raw` keeps each session's full Codex log in `<results>/raw/`. These logs hold absolute
  paths; do not publish them.
- **Cost.** The 60 recorded sessions cost $0.27 at the list prices in `rates.yaml`. Rescoring new designs costs a
  few cents in judge and embedding calls.

The operator's full procedure, including how the briefs and the references were fixed before the runs, is in
`RUNNING.md`.
