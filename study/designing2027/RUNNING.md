# Running the Designing 2027 sessions

This guide takes you from the case files to committed results, in four phases: set up, a smoke test, the pilots
and the full run. Each step says what to run, what you should see, and what to send back before the next step.

**What the study does.** A coding agent (Codex) uses the `ddspace-search` or `ddspace-explain` skill on six cases
built from the CAIN briefs (`cases/`) and writes one rationale file per session, under three conditions:

| Condition | The agent's working folder | The skill |
|---|---|---|
| **M** | the C1 design space mined by ddspace, as a wiki | with the space reference (`ddspace query`, `ddspace point`) |
| **E** | the C1 expert decision model, as a wiki | the same |
| **N** | only the problem (and the solution, in explain) | zero-shot: the agent's own knowledge, `space: null`; points described by `ddspace point --no-space` |

| Case | Skill | Brief |
|---|---|---|
| `fraud-search` | search | card-fraud scoring |
| `fraud-explain` | explain | card-fraud scoring, with a solution to explain |
| `vision-search` | search | on-device visual inspection |
| `forecast-search` | search | retail demand forecasting |
| `documents-search` | search | large-scale document classification |
| `documents-explain` | explain | document classification, with a solution to explain |

6 cases × 3 conditions × 2 repetitions = **36 sessions**. The paper may report a subset (two search and two
explain cases).

**Time and cost.** About 30 minutes of setup. A session takes 5 to 30 minutes; the full run takes 4 to 10 hours,
and it can be stopped and resumed. Expect roughly $1 to $3 per session for the agent, as in CAIN, plus a few cents
per session for the descriptions `ddspace point` writes in M and E (on the study key).

## 0. Before you start

You need:

- the repository on the branch `study/designing2027-sessions`, with the package installed in editable mode, so
  the skills and the checker the sessions use are this branch's;
- the conda environment `taxonomy`;
- Codex CLI (the last check used `codex-cli 0.165.0`), logged in;
- the **study key**: an OpenAI key with a low spending limit, used only by `ddspace point` inside M and E
  sessions. Revoke it when the study is done.

```bash
cd ~/Documents/GitHub/delve
git switch study/designing2027-sessions
conda activate taxonomy
pip install -e . --quiet
codex --version
```

Every command below runs from this folder, with `taxonomy` active.

**The sandbox.** The agent must not see the repository, so everything it touches lives in
`~/Documents/GitHub/ddspace-sandboxes/designing2027` (next to the CAIN sandbox; `ddspace-sandboxes` is the
`.nosync` link you set up for CAIN, so iCloud does not sync it). The runner refuses a `--workspaces` or
`--scratch` folder inside the repository.

**Reasoning effort.** Every command passes `--effort high`: the runner ignores your own Codex settings, and
at the model's default effort the pilots gave up halfway. Keep one effort for the whole study; the runner records
it per session and refuses to mix two in one results folder.

## 1. Build the workspaces

```bash
python study/cain2027/build_workspaces.py build --out ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces
```

This writes `N/` (empty), `M/` (the mined space) and `E/` (the expert model), each M and E with its wiki. It
takes under a minute. Check both wikis:

```bash
(cd ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces/M && ddspace wiki check)
(cd ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces/E && ddspace wiki check)
```

**You should see** two passing checks (351 and 163 files). If the builder says an input changed, restore it with
`git checkout study/cain2027/inputs/`.

Then give the study key to this terminal (repeat in any new terminal):

```bash
export STUDY_OPENAI_API_KEY=sk-...your study key...
```

**Run log.** Start `study/designing2027/RUNLOG.md` with the output of:

```bash
date; git rev-parse --short HEAD; codex --version
```

and the model, `gpt-6-luna`. Add a line whenever something changes (a skill revision after the pilots, a
rerun).

## 2. Smoke test: does Codex find the skill?

One session, `fraud-search` on M, kept in its own results folder:

```bash
python study/designing2027/run_sessions.py \
  --workspaces ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces \
  --scratch ~/Documents/GitHub/ddspace-sandboxes/designing2027/scratch \
  --model gpt-6-luna --effort high --cases fraud-search --conditions M --reps 1 \
  --results results-smoke --keep-raw --timeout 3600
```

**You should see** a first line with the Codex version, the model and `skills via files`, then
`fraud-search-M-r1: started`, and progress lines while the agent works, each with the time since the start:

```
    [00:42] ddspace query dimensions
    [01:10] ddspace query values d:21
    [06:35] ddspace point v:21.7 v:43.2
    [14:02] wrote fraud-search.json
    [14:20] ddspace rationale check rationale/fraud-search.json  (exit 1)
    [15:05] ddspace rationale check rationale/fraud-search.json
    [15:30] the agent finished
```

A check that ends with `(exit 1)` found problems, which the agent then fixes: that is normal. When nothing has
happened for two minutes, a `still running (N commands so far)` line shows the session is alive. The session ends
with `fraud-search-M-r1: ok; check ok, N check runs`.

**Did the agent use the skill?** It did if all of these hold:

```bash
grep -c "ddspace-search/SKILL.md" study/designing2027/results-smoke/raw/fraud-search-M-r1.jsonl
python -c "import json; d=json.load(open('study/designing2027/results-smoke/rationale/fraud-search-M-r1.json')); print(d['schema'], len(d['approaches']), len(d['points']), sorted({s['round'] for s in d['trajectory']}))"
```

- the first command prints a number above 0 (the agent read the skill file);
- the second prints `ddspace-rationale/5`, two or more approaches, some points, and rounds such as `[1, 2, 3]`.

**If the skill was not used** (the count is 0 and the file has no approaches or rounds), run the same command
with `--skills-via prompt --results results-smoke-prompt`, and check again. Whichever works is the setting for
every later step; write it in the run log.

**Send me:** the line the runner printed and which setting worked. I read
`results-smoke/summaries/fraud-search-M-r1.json` and the explainer in `results-smoke/explainers/` from here.

## 3. Pilots: four sessions, then a read

```bash
python study/designing2027/run_sessions.py \
  --workspaces ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces \
  --scratch ~/Documents/GitHub/ddspace-sandboxes/designing2027/scratch \
  --model gpt-6-luna --effort high --cases fraud-search --conditions M,E,N --reps 1 \
  --results results-pilot --keep-raw --timeout 3600
python study/designing2027/run_sessions.py \
  --workspaces ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces \
  --scratch ~/Documents/GitHub/ddspace-sandboxes/designing2027/scratch \
  --model gpt-6-luna --effort high --cases fraud-explain --conditions M --reps 1 \
  --results results-pilot --keep-raw --timeout 3600
```

(Add `--skills-via prompt` to both if the smoke test needed it.)

**You should see** four `ok` lines with a clean check. Open the explainers: each is
`study/designing2027/results-pilot/explainers/<session>/explainers/<case>.html`. Read each one for:

- search: are the alternatives really different, and does every requirement drive a choice or appear under
  "Requirements not addressed" with a reason?
- explain: is every decision of the solution mapped onto the space or listed under the gaps, and are the forced
  and free choices plausible?
- M and E: do the gaps at the bottom of the page make sense?
- N: does the page say no space was provided, and are the agent's own dimensions sensible?

**Send me** what you noticed. If the skills need changes, I make them on `feat/rationale-search-explain` and merge
them here; then delete `results-pilot` and run the pilots again. Once the pilots are fine, the skills are frozen:
note the commit in the run log.

## 4. The full run: 36 sessions

Delete the pilot's raw logs (large, never committed):

```bash
rm -rf study/designing2027/results-pilot/raw study/designing2027/results-smoke*/raw
```

Then run every session (add `--skills-via prompt` if the smoke test needed it):

```bash
python study/designing2027/run_sessions.py \
  --workspaces ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces \
  --scratch ~/Documents/GitHub/ddspace-sandboxes/designing2027/scratch \
  --model gpt-6-luna --effort high --timeout 3600
```

- **Order:** case by case (`fraud-search` under M, E, N, both repetitions, then the next case), so a partial run
  still covers every condition of the first cases.
- **Stopping and resuming:** Ctrl+C, then the same command. Sessions with a kept result and `status: ok` are
  skipped; failed ones run again.
- **A session that keeps failing:** note it in the run log and tell me; do not delete it silently.
- The runner refuses to mix sessions of two prompt or skill versions in one results folder: if the skills change
  mid-run, start a new folder (`--results results-v2`).

**Send me** the final lines once all 36 show `ok` (or which ones failed). Results are in
`study/designing2027/results/`: `rationale/` (the files), `summaries/` (checks, commands, cost) and `explainers/`.

## 5. Commit the results

I check the kept files for secrets and absolute paths before committing (the runner already redacts the home
folder and the study key). Never commit `raw/` or the sandbox; the ignore rules keep `results*/raw/` out.

When the study is done, revoke the study key.

## 6. The second run: trade-offs (schema 6)

After the toy runs (2026-11-09), the skills record trade-offs: every point description ends with its own
`Trade-off: …`, and every step names its trade-offs against the requirements, each with the values that cause
it. N now describes its points too (`ddspace point --no-space`), with the M wiki's model, so **every** session
gets network access and the study key; the runner prints the describer model per session (`describer` in the
summary). The first 36 sessions stay in `results/` as the "before" run.

Add a line to the run log (`date; git rev-parse --short HEAD`), then the same command as section 4, with a new
results folder:

```bash
python study/designing2027/run_sessions.py \
  --workspaces ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces \
  --scratch ~/Documents/GitHub/ddspace-sandboxes/designing2027/scratch \
  --model gpt-6-luna --effort high --timeout 3600 --results results-v2
```

To try it on one session first (about 5 minutes):

```bash
python study/designing2027/run_sessions.py \
  --workspaces ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces \
  --scratch ~/Documents/GitHub/ddspace-sandboxes/designing2027/scratch \
  --model gpt-6-luna --effort high --timeout 3600 --results results-v2-smoke \
  --cases fraud-explain --conditions N --reps 1
```

**You should see** `fraud-explain-N-r1: ok; check ok`, and in the progress lines `ddspace point --no-space …`
calls. Send me that line; I check the summary's `points_evaluated` before you start the full run.

