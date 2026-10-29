# Running the study

This guide takes you from the design briefs to committed, reproducible results. Each step says what it does,
what you should see, and what to do if it goes wrong. The criteria used to validate the results (steps 3, 8 and
9) are explained in `VALIDATION.md`.

**What the study does.** A coding agent (Codex) writes Architecture Decision Records (ADRs) for four ML-enabled
systems described in short briefs, under three conditions:

- **N**: the brief only;
- **M**: the brief plus the design space mined by ddspace from the C1 sources;
- **E**: the brief plus the C1 expert decision model, as a design space.

There are 4 briefs, 3 conditions and 2 repetitions, so 24 sessions in all. The ADRs are then scored against the
expert model and rated blind by two people.

**Time and cost.** About 30 minutes of setup, then 5 to 15 minutes per session, so 2 to 6 hours for the full run
(it can be stopped and resumed). Expect roughly $1 to $3 per session, plus a few cents for scoring.

## 0. Before you start

You need:

- the repository, on the branch `feat/cain-agent-study`;
- the conda environment `taxonomy` (it has ddspace and the study's Python packages);
- Codex CLI, installed and logged in;
- two OpenAI API keys:
  - a **study key**: a new key with a low spending limit, used only by the agent's tools during the sessions;
    revoke it when the study is done;
  - your **scoring key**, used by the scorer (embeddings and the judge model).

Open a terminal and run, one line at a time:

```bash
cd ~/Documents/GitHub/delve
git switch feat/cain-agent-study
conda activate taxonomy
codex --version
```

The last command should print a version, such as `codex-cli 0.163.0`. If it says `command not found`, install
Codex. If Codex asks you to log in when you use it, run `codex login` first.

Every command below is run from this folder (`~/Documents/GitHub/delve`), with `taxonomy` active.

### The sandbox folder

The agent must not see this repository: it holds the expert model and the scoring code. So the study works in
a separate folder outside the repository, called the **sandbox** here:
`~/Documents/GitHub/ddspace-sandboxes/cain2027`, next to the repository. Use the same folder throughout. You do
not need to create the `cain2027` folder: step 2 does.

`~/Documents` is synced by iCloud. The sandbox must not be: each session briefly holds a copy of your Codex
login, and iCloud sync can duplicate or damage files that change often. So the real folder is named
`ddspace-sandboxes.nosync` (iCloud skips folders whose names end in `.nosync`), and `ddspace-sandboxes` is a link
to it. To set this up on a new machine:

```bash
mkdir -p ~/Documents/GitHub/ddspace-sandboxes.nosync
ln -s ddspace-sandboxes.nosync ~/Documents/GitHub/ddspace-sandboxes
```

## 1. Finalize the briefs

The briefs are in `study/cain2027/briefs.yaml`. Each one has:

- `text`: what the agent reads. Describe the system and its requirements in plain words. Do not use the names
  of options from the expert model (such as "model as a service"): that would hint at the answer.
- `forces`: the requirements that matter most for this system, as force ids from the expert model. The agent
  never sees them; they are used for scoring.

To see the force ids you can use:

```bash
python study/cain2027/reference.py --forces
```

When the briefs are final, change `draft: true` to `draft: false` at the top of the file.

Optional: for the cost figures, fill in `study/cain2027/rates.yaml` with the model's price per million tokens and
the date you looked it up.

## 2. Build the three workspaces

```bash
python study/cain2027/build_workspaces.py build --out ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces
```

**What it does.** It creates three folders in the sandbox, one per condition:

- `N/`: empty;
- `M/`: the mined design space, as a wiki, with a guide for the agent (`AGENTS.md`);
- `E/`: the expert model, as a wiki, with the same kind of guide.

There is no separate step for the C1 wiki: this command builds it, from the files in `study/cain2027/inputs/`.

**Check it.** Run the wiki check in both design-space workspaces:

```bash
cd ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces/M
ddspace wiki check
ddspace query dims --table
cd ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces/E
ddspace wiki check
cd ~/Documents/GitHub/delve
```

Both checks should pass. The table lists the dimensions of the mined design space (32; the expert model has
28). To browse a wiki, run `ddspace wiki open` inside its folder.

**If it fails** with a message about changed inputs, a file in `study/cain2027/inputs/` differs from the
recorded version. Restore it with `git checkout study/cain2027/inputs/`.

## 3. Write the expert reference

```bash
python study/cain2027/reference.py
```

**What it does.** It first checks the briefs: every force id must exist in the expert model and affect at least
one expert decision. Then, for each brief, it writes `study/cain2027/references/<brief>.md`. This file lists the
expert decisions that matter for the brief's forces, with their options ranked from best to worst for those
forces. The best options are in bold.

**You should see** one line per brief, such as `fraud: 18 relevant decisions`.

**Read the references as part of reviewing the briefs.** If a brief makes almost all 28 decisions relevant, it
does not tell good designs from weak ones; choose fewer or more specific forces. Each time you change the
briefs, run this step again.

**Commit the references before any session runs** (see step 10). This records the yardstick before any
results exist.

## 4. Prepare the session settings

Choose **one Codex model** for all sessions, such as `gpt-6-luna`, and keep it for the whole study. It cannot
be `gpt-5.4-mini`, the model the scorer uses as a judge: the runner refuses it, so the judge never grades
its own output.

Give the study key to this terminal:

```bash
export STUDY_OPENAI_API_KEY=sk-...your study key...
```

The key stays in this terminal window only. If you open a new terminal, repeat the `export` (and
`conda activate taxonomy`).

Notes:

- Each session runs in a fresh copy of its workspace, with a private copy of your Codex login and nothing else
  from your Codex settings, and with web search and other online tools turned off.
- The `taxonomy` Python runs as an Intel program on Apple silicon (through Rosetta). The runner takes care of
  starting Codex as a native program, so you do not need to do anything about it.

### Keep a run log

Write down the following before the pilot, and again before the full run if anything changed. They make the
run reproducible. Use `study/cain2027/results/RUNLOG.md` (committed with the results):

```bash
date
git rev-parse --short HEAD
codex --version
```

Also record the model name. The runner adds, per session, the model, the start time and fingerprints of the
prompt and the output format (in `results/summaries/`).

## 5. Pilot: one brief, three conditions, one repetition

Run three sessions first (the `fraud` brief under N, M and E) to check that everything works:

```bash
python study/cain2027/run_sessions.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --scratch ~/Documents/GitHub/ddspace-sandboxes/cain2027/scratch --model gpt-6-luna --briefs fraud --reps 1 --keep-raw
```

The options are:

- `--workspaces`: the folder from step 2;
- `--scratch`: where each session's working copy goes; created if missing;
- `--model`: the Codex model from step 4;
- `--briefs fraud --reps 1`: only the `fraud` brief, one repetition;
- `--keep-raw`: keep Codex's full logs, to look into problems.

**You should see** one line per session, ending in `ok`, after a few minutes each.

**Check the results.**

- `study/cain2027/results/adrs/fraud-N-r1/` (and `-M-`, `-E-`): the ADRs, as Markdown. Read them: they are what
  the study is about.
- `study/cain2027/results/summaries/fraud-M-r1.json` (and `-E-`): `status` is `ok`, `ddspace_calls` lists the
  tool commands the agent ran, `points` lists the design points it explored, and `network_commands` and
  `web_search` are 0.

**If a session fails**, its line gives the reason. The detailed log is in
`study/cain2027/results/raw/<session>.stderr.txt`. Run the same command again: sessions that already succeeded
are skipped, and failed ones are retried. If a point in a summary shows `"ok": false`, the study key did not
reach the tools; check the `export` from step 4.

### Score the pilot and check the judge

The scorer matches the agent's options to the expert options with a judge model. Check it by hand once, on the
pilot:

```bash
export OPENAI_API_KEY=sk-...your scoring key...
python study/cain2027/score.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --export-labels
```

This writes `study/cain2027/results/labels/<session>.csv`. Each row is an option the agent considered, with its
`best_match` (the expert option the score uses, with the judge's label) and its `other_matches` (used only by the
lenient variant). Write `y` or `n` in the last column: does the best match name the same design option? Leave it
empty when there is no best match. Then record the share of `y` (the matcher's precision) and the date as a line
in the CAIN entry of `benchmark/README.md`.

Running `score.py --export-labels` again overwrites these files: once you start filling them in, score without
`--export-labels`.

**Decide** whether to go ahead with the full run. If the ADRs or the matches look wrong, stop and fix the setup
first.

## 6. The full run: 24 sessions

Delete the pilot's raw logs (they are large and not kept):

```bash
rm -rf study/cain2027/results/raw
```

If you changed the prompt, the model or the briefs after the pilot, also delete the pilot's results, so that
the study does not mix two setups:

```bash
rm -rf study/cain2027/results
```

Then run all sessions. This is the pilot command without `--briefs`, `--reps` and `--keep-raw`:

```bash
python study/cain2027/run_sessions.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --scratch ~/Documents/GitHub/ddspace-sandboxes/cain2027/scratch --model gpt-6-luna
```

- **Stopping and resuming:** you can stop with Ctrl+C and run the same command later. Sessions that already
  have a result are skipped.
- **A failed session** does not stop the others. Run the command again to retry it.
- **Rerunning one session** on purpose: delete its file in `study/cain2027/results/designs/` (for example
  `fraud-M-r2.json`) and run the command again.
- **Timeout:** a session that takes more than 30 minutes is stopped and counted as failed (`--timeout 3600`
  allows an hour).

At the end, every one of the 24 sessions should show `ok`. Report any session that keeps failing, rather than
leaving it out silently.

## 7. Score all sessions

```bash
export OPENAI_API_KEY=sk-...your scoring key...
python study/cain2027/score.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces
```

**What it does.** It compares every session's ADRs with the expert model and writes
`study/cain2027/results/scores.json`. This file holds one row per session, and a mean, minimum and maximum per
condition, of:

- decision coverage (all expert decisions) and relevant-decision coverage (those of the brief's reference). Each
  of the agent's options counts through its best match only; the `_same` and `_lenient` variants count more
  loosely, and the gap shows how much a lenient matcher would inflate coverage;
- requirements fit, with `fit_decisions`: the number of decisions it is computed on (report them together);
- driver recall;
- grounding and consistency (M and E only);
- design points explored, and cost.

While it runs, it prints one line per session, such as
`[12/60] fraud-M-r2: 1450 matches (210 judged), relevant coverage 0.28, 35 s`. Sessions scored before go fast:
the judge's verdicts are cached in `results/judge_cache.json`, so a second run gives the same numbers without
new calls.

## 8. Blind rating

Two people rate the ADRs without knowing which condition produced them. The rating uses repetition 1 of every
brief and condition: 12 sets of ADRs.

### Build the rating kit

```bash
python study/cain2027/rating.py packets --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --seed 2027
```

The `--seed` makes the kit reproducible: the same seed gives the same codes and order. It creates:

- `study/cain2027/results/rating/packets/P###.md`: one packet per ADR set, each with a random code: the brief,
  then the ADRs. Identifiers that would reveal the condition (value ids, citations) are removed.
- `study/cain2027/results/rating/RUBRIC.md`: the four items to rate, each from 1 (poor) to 4 (good).
- `study/cain2027/results/rating/sheet-A.csv` and `sheet-B.csv`: one rating sheet per rater, with the packets in
  a different order.
- `study/cain2027/results/rating-key/key.json`: which packet comes from which session. **Do not open it until
  both sheets are complete.**

If the command lists packets that "mention the design space", open those packets. If the wording gives the
condition away (for example, "according to the design space..."), reword that sentence by hand and note it in
the run log.

### Rate

Give each rater the `packets` folder, `RUBRIC.md` and their own sheet. Each rater fills in their sheet in a
spreadsheet program, alone, and saves it as CSV under the same name.

### Agreement

```bash
python study/cain2027/rating.py agreement
```

This prints, per item, the agreement between the raters (quadratic-weighted Cohen's kappa: 1 is perfect, 0 is
chance), and lists the cases where the two raters differ by 2 points or more.

Discuss those cases together and agree on a score. Save a copy of one sheet with the agreed scores as
`study/cain2027/results/rating/sheet-resolved.csv`.

### Unblind

```bash
python study/cain2027/rating.py agreement --unblind
```

This adds the mean scores per condition, from the two raters' original scores and from the agreed ones. Everything is
saved in `study/cain2027/results/rating/agreement.json`.

To build a new kit (only before anyone has rated), delete `study/cain2027/results/rating` and
`study/cain2027/results/rating-key`, then build again.

## 9. Read the results

- `results/scores.json`: the measured results per condition (step 7).
- `results/rating/agreement.json`: the human ratings per condition (step 8).
- `results/adrs/`: the ADRs of each session. For the paper's example, compare the three conditions of one
  brief side by side.

`VALIDATION.md` explains each measure and the caveats to report.

## 10. Commit

Commit in two moments.

**Before any session runs:** the final briefs and their references.

```bash
git add study/cain2027/briefs.yaml study/cain2027/references
git commit -m "study(cain): final briefs and expert references"
```

**After the study:** the results.

```bash
git add study/cain2027/results
git status
git commit -m "study(cain): session results, scores and ratings"
```

Check the `git status` list before committing. It should show `designs/`, `summaries/`, `adrs/`, `labels/`,
`rating/`, `rating-key/`, `scores.json`, `judge_cache.json` and `RUNLOG.md`. Raw logs (`results/raw/`) are
excluded automatically.

Before publishing the results (for example, on the anonymous artifact branch), search them for your name and
your home folder path. The summaries are cleaned automatically, but the ADRs are free text:

```bash
grep -ril "$(whoami)" study/cain2027/results
```

The command should print nothing.

When the study is done, revoke the study key in the OpenAI dashboard.

## 11. More repetitions

Five repetitions per brief and condition instead of two, decided after reading the first 24 sessions (see
`VALIDATION.md`). Run in the same terminal setup as before (step 0, and the study key from step 4):

```bash
python study/cain2027/run_sessions.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --scratch ~/Documents/GitHub/ddspace-sandboxes/cain2027/scratch --model gpt-6-luna --reps 5
```

Sessions that already have a design are skipped, so this runs only the missing repetitions. Then score as in
step 7 and commit as in step 10.

## 12. Rerunning with the MADR-title prompt

After the first results, the prompt was changed to ask for MADR titles (a statement that names the problem and
the chosen solution) instead of a title or question. The earlier run, kept in `results-question-titles/`, used
the earlier wording. Its Markdown ADRs already show solution titles: when the agent wrote a question, the ADR's
title is the chosen option and the question is shown below it.

The runner refuses to add sessions to a folder made with another version of the prompt. To rerun with a new
prompt, first move the recorded results aside, keeping their judge cache for the new scoring:

```bash
git mv study/cain2027/results study/cain2027/results-<label>
mkdir -p study/cain2027/results
cp study/cain2027/results-<label>/judge_cache.json study/cain2027/results/
```

Then run with `--reps 5` (step 11) and score (step 7). The decision titles are part of what the matcher compares,
so scores from different prompt versions are not comparable; report which prompt version the paper uses.

## 13. A second agent model (Ollama Cloud)

To check that the results do not depend on one model, the same study can be run with another agent model.
Only the agent changes; the judge stays the same. With Ollama Cloud (signed in, with your Ollama API key in
the environment):

```bash
python study/cain2027/run_sessions.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --scratch ~/Documents/GitHub/ddspace-sandboxes/cain2027/scratch --model beam:cloud --oss ollama --results results-beam --briefs fraud --reps 1 --keep-raw
```

- `--oss ollama` runs the model through Ollama (`codex --oss --local-provider ollama`); only the `OLLAMA_*`
  variables reach the session, besides the usual ones.
- `--results results-beam` keeps this model's sessions apart: one results folder holds one agent model, and the
  runner refuses to mix them.
- Sessions run one at a time, so Codex makes one model call at a time (the free tier allows 3 concurrent calls).
- Each summary records the model, the provider and the Codex version.

Start with this pilot (one brief, three sessions). If all three are `ok` and the M and E sessions show
`ddspace` calls and design-point checks, drop `--briefs fraud --reps 1 --keep-raw` and add `--reps 5`. Then score:

```bash
python study/cain2027/score.py --workspaces ~/Documents/GitHub/ddspace-sandboxes/cain2027/workspaces --results results-beam
```

The scorer starts from a copy of `results/judge_cache.json`, so pairs judged before keep their verdicts.
