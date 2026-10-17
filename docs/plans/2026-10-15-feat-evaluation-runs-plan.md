---
title: "feat: evaluation runs — feedback switch, long-context and prior-knowledge baselines, main runs and ablations"
type: feat
status: accepted (2026-10-15); plan only, no code changed yet; decisions on the open questions recorded below
date: 2026-10-15
related: >-
  src/taxonomy_generator/utils.py (format_feedback), src/taxonomy_generator/settings.py (EvaluationSettings),
  src/taxonomy_generator/pipeline_cli.py (--match-gt), benchmark/README.md, examples/{c1-ml-workflow,c2-rl-monitoring,c3-git-at-scale}/
---

# Evaluation runs

## Goal

Produce the evaluation's results with the current pipeline. This plan lands on `feat/ddspace-tool`. The user
merges that branch into `main` first, and steps 1 and 2 are then implemented on a branch from `main` (user
decision, 2026-10-15). The steps, in order:

1. **(b) feedback switch.** An ablation switch: the Critic's scoreboard is computed but not fed back. Plus a test.
2. **L1 and L5 baselines.**
   - L1, long-context generation: the whole corpus in one prompt.
   - L5, prior-knowledge probe: the use case only.
3. **Merge** `feat/ddspace-tool` into `main` (a PR; the user publishes).
4. **Smoke run** on the merged `main`.
5. **Main runs, then the ablations,** all sequential, each followed by matching.

What each comparison answers:

| Comparison | Question |
|---|---|
| Delve vs L1 | Does the multi-step workflow recover more of the expert models than one long prompt? |
| Delve vs L5 | How much of the agreement comes from reading the corpus rather than from what the model already knows? Both expert studies are published |
| Delve vs (b) | Does the Critic's feedback loop improve the result? |
| Delve vs (c) rewrite | Do validated editing operations keep alternatives that whole-model rewriting loses? |

Ablation (a), no open coding, is out of scope (user decision, 2026-10-15). The evaluation describes it as future
work.

## Fixed setup (applies to every run)

- **Pipeline:** `main` after the merge. Its defaults differ from the 2026-10-02 runs:
  - value recoding is on;
  - the dimension cap is applied at selection;
  - the exclusivity row is in the scoreboard and fed back;
  - matching uses `gpt-5.4-mini`.

  The 2026-10-02 runs are therefore not mixed into the result tables.
- **Models:** generation and evaluation `openai/gpt-5.6-luna`; matching `openai/gpt-5.4-mini` (independent of
  the generator). The baselines use the generation model.
- **Seeds:** `pipeline.random_seed` 42, 43, 44. The seed controls the minibatch order only; the provider's outputs
  are not deterministic. Comparisons with an ablation or a baseline are **paired by seed**.
- **One run at a time:** never several full runs in parallel (a 4M tokens-per-minute limit was hit before).
- **Outputs:**
  - `output/evaluation/<case>/<variant>_s<seed>/`, which is gitignored;
  - the open codes and documents of each run are kept locally, so replays remain possible;
  - downloaded source texts are never committed.

## Step 1: the (b) feedback switch (code)

- **Setting:** `evaluation.loop_feedback: bool = True` in `EvaluationSettings`, read in `_build_evaluation`, and
  exposed on `Configuration` like the other evaluation fields.
- **Behavior when `false`:**
  - [`format_feedback`](../../src/taxonomy_generator/utils.py) leaves out the evaluation section, which holds the
    judged criteria and the **exclusivity row**;
  - the scoreboard is still computed, saved in `evaluation_history` and reported;
  - unchanged: external feedback (the `feedback:` config section) and the saturation critic's text, which also
    drives the stopping rule.

  This is ablation (b) as the evaluation design defines it: the scoreboard is computed but not passed to the next
  update.
- **Run record:** the taxonomy JSON holds enough provenance (user decision, 2026-10-15). There is no separate run
  record. Check only that a run's settings show `loop_feedback`; if not, add it where the edit mode is recorded
  (`_add_edit_record`).
- **Tests:**
  - `format_feedback` with `loop_feedback` false has no evaluation section, but keeps the saturation and external
    feedback;
  - with true, the output is unchanged (an existing test, or a new snapshot);
  - the setting parses from YAML, and the default is true.
- **Ablation configs:** `examples/c1-ml-workflow/c1_ml_workflow_nofeedback_config.yaml` and the C2 equivalent.
  Copies of the study configs with `loop_feedback: false` and `name: "…-nofeedback"`. Nothing else changes.
- **Done when** the unit tests pass, and a C3-sample run with `loop_feedback: false` shows scoreboards in
  `evaluation_history` but no evaluation section in the update prompts (checked in the log).

## Step 2: the L1 and L5 baselines (code)

- **Script:** `benchmark/baselines.py --case c1-ml-workflow --kind long_context|prior_knowledge --seed N`, one
  LLM call per run.
  - **Prompt:** the case's use case (from its config), the same output contract as Delve (dimensions as decision
    points, values as candidate decisions with status accepted, rejected or mixed, outcomes apart, descriptions),
    and the same terminology.
  - **L1** adds every passage of the case's corpus, with its passage id (`sNN_pKK`).
  - **L5** adds no corpus, and asks explicitly for the decision points and alternatives the model knows for this
    use case.
  - **Structured output:** reuse `TaxonomyOutput`, so the result has Delve's shape.
- **Output:** a taxonomy JSON with `mode: "baseline-l1"` or `"baseline-l5"`; `iterations: [{clusters}]` and
  `selected_clusters` set to the same list; `run_metrics` (tokens, elapsed time); the model; a prompt
  fingerprint. `python main.py --match-gt <file> --gt benchmark/<case>/gt` then scores it like any run.
- **Context check (L1)**, measured 2026-10-15 with `o200k_base`:

  | Case | Corpus |
  |---|---|
  | C1 | 265 passages, ~86.7k tokens |
  | C2 | 243 passages, ~80.6k tokens |
  | C3 | 48 passages, ~17.4k tokens |

  - Before running, confirm the generation model's context window and maximum output, and record both.
    **Confirmed 2026-10-16 (user):** `gpt-5.6-luna` has a 1,050,000-token context window and a 128,000-token
    maximum output. The largest L1 prompt (C1, ~88k) fits with ample room; the script's `--max-input-tokens`
    guard stays at 200,000.
  - If a corpus does not fit with the prompt and room for output, stop and decide (e.g. summaries instead of
    passages). Don't silently truncate.
- **Repetitions:** 3 per case and baseline (calls are cheap), reported as mean and range like Delve's seeds. The
  seed has no effect on a single call, so it only labels the repetition.
- **Cases:** C1 and C2, which have expert models. C3 has none, so it gets no baseline.
- **Tests:**
  - prompt assembly: L1 contains every passage id, L5 contains none;
  - the output passes `load_seed_taxonomy`;
  - `--match-gt` runs on a small fake output.
- **Done when** each baseline produces a scored file for C1 and C2.

## Step 3: merge

- `feat/ddspace-tool` is fully pushed, and `main` is its ancestor (44 commits), so the PR merges without conflicts.
- After the merge, work from `main` or a new branch. Do not check out old commits that still track now-ignored
  local folders: that would overwrite them.
- Decided: this plan is the last commit on `feat/ddspace-tool`. After the merge, steps 1 and 2 are built on a
  branch from `main`, and steps 4 and 5 run from that code.

## Step 4: smoke run

- **C3 sample** (`examples/c3-git-at-scale/c3_git_at_scale_sample_config.yaml`). It is the smallest case and
  exercises the whole pipeline: open coding, tools-mode updates, critic, saturation, consolidation with recoding,
  selection, final scoreboard.
- **Plus one feedback-switch run** on the same sample (step 1's done-check), and **one L5 call** for C2 (cheap),
  matched.
- **Check:**
  - no errors;
  - the scoreboard has the exclusivity row;
  - `operation_log` has a recoding entry;
  - matching works with `gpt-5.4-mini`;
  - tokens and time are as expected.

## Step 5: runs, then matching

Run order: the main runs first, because they are the results everyone needs. Then the ablations and baselines.

| # | Case | Variant | Seeds | Config |
|---|---|---|---|---|
| M1–M3 | C1 | full | 42, 43, 44 | `c1_ml_workflow_config.yaml` |
| M4–M6 | C2 | full | 42, 43, 44 | `c2_rl_monitoring_config.yaml` |
| M7–M9 | C3 | full | 42, 43, 44 | `c3_git_at_scale_config.yaml` |
| B1–B12 | C1, C2 | L1 × 3, L5 × 3 each (one row per call) | 42, 43, 44 | `benchmark/baselines.py` |
| A1–A2 | C1, C2 | (b) no feedback | 42 | `*_nofeedback_config.yaml` |
| A3–A4 | C1, C2 | (c) rewrite | 42 | copies with `edit_mode: rewrite` (`*_rewrite_config.yaml`) |
| A5–A8 | C1, C2 | (b) and (c) | 43 | only if time allows (a second paired seed) |

- **Runner:** `benchmark/run_matrix.py` (Python rather than bash, for the config copies and the CSV;
  `--list` shows the rows, `--dry-run` prints the commands; smoke rows S1–S3). For each row, in order:
  1. write a seed-specific copy of the config (`random_seed: N`; `name` with the variant and seed) into the run's
     output folder;
  2. run `python main.py --corpus <corpus> --config <copy> --output <dir>`;
  3. run `python main.py --match-gt <taxonomy> --gt benchmark/<case>/gt` (both views; `gpt-5.4-mini` from the
     config);
  4. append a line to `output/evaluation/runs.csv`: id, case, variant, seed, status, tokens, elapsed time, the
     taxonomy path, the match path.

  The runner stops on a failure and does not skip ahead. A failed run is recorded and retried once; failures are
  reported, not hidden.
- **C3:** no expert model, so it is not matched. Three seeds (user decision, 2026-10-15) give its **stability**,
  as for C1 and C2.
  - Stability is measured as the spread of the intrinsic metrics over seeds (scoreboard, exclusivity,
    generality, counts), plus the pairwise alignment of the seeds' outputs: their dimensions and values matched
    to each other with the same matcher, using one seed's output as the reference.
  - C3's outputs also feed the qualitative part (design points, the wiki).

### Budget

From the 2026-10-02 and 2026-10-15 runs:

| Case | Time per run | Tokens per run |
|---|---|---|
| C1 | ~73 min | ~8.3M |
| C2 | ~34 min | ~3.7M |
| C3 | ~25 min | ~1.5M |

| Block | Runs | Time | Tokens |
|---|---|---|---|
| Smoke (C3 sample, switch run, one L5) | 3 | < 1 h | < 2M |
| Main M1–M9 | 9 | ~6.6 h | ~40.5M |
| Baselines B1–B12 | 12 calls | < 0.5 h | ~1.1M (L1: ~85k input × 6) |
| Ablations A1–A4 | 4 | ~3.6 h | ~24M |
| Optional A5–A8 | 4 | ~3.6 h | ~24M |
| Matching | per matched run | ~minutes each | small (mini model) |

Without the optional rows: about 11–12 hours of sequential runs and about 68M tokens. Rewrite-mode runs may cost
differently from tools mode; the actual numbers are recorded.

### Timeline (deadline 2026-10-23)

| Day | Work |
|---|---|
| 10-15 / 16 | Step 3 (merge, by the user); then on a branch from `main`: step 1 (switch and test), step 2 (baselines and tests) |
| 10-16 | Step 4 (smoke) |
| 10-16 → 17 | M1–M9 (overnight possible) |
| 10-17 → 18 | B1–B12, A1–A4 |
| 10-19 | Abstract (does not need final numbers) |
| 10-19 → 20 | Analysis, tables, optional A5–A8 |
| 10-21 → 23 | Writing |

## Results checklist (per run)

- [ ] The taxonomy JSON is in `output/evaluation/<case>/<variant>_s<seed>/`, with `run_metrics` and the
  configuration.
- [ ] Open codes and documents are kept locally.
- [ ] Match file for both views (paper and model). Option and decision F1, exact recall.
- [ ] Final scoreboard (with the exclusivity row), exclusivity and generality.
- [ ] A line in `runs.csv`.
- [ ] Failures and retries noted.

## Risks

| Risk | Mitigation |
|---|---|
| A rate limit or provider error mid-run | One run at a time; the runner stops and records; a single retry |
| A run takes far longer than budgeted | Main runs first; optional rows are dropped first |
| L1's corpus is too close to the context limit | Measured above; confirm the window first; no silent truncation |
| L5 scores high (memorization) | That is a finding to report, not a failure; it qualifies the RQ1 claims |
| Merged defaults differ from what the write-up describes | Check the method description against `config.yaml` and the study configs before writing the results |
| iCloud interferes with git or output folders | Check for " 2" duplicates and lost refs if git behaves oddly; outputs live under `output/` |

## Decisions (2026-10-15)

1. **C3:** three seeds, like C1 and C2, to evaluate stability.
2. **Run record:** the taxonomy JSON already records enough.
3. **Branch:** this plan stays on `feat/ddspace-tool`. After the merge into `main`, the work continues from
   `main`.
