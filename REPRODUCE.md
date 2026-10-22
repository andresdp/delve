# Reproducing the results

There are three levels, from cheapest to most expensive.

| Level | What | API key | Time | Cost |
|---|---|---|---|---|
| 1 | Recompute every table and number from the stored runs | no | minutes | none |
| 2 | Rerun the LLM-judged checks on the stored runs | yes | about an hour | a few dollars |
| 3 | Rerun the case studies, baselines and ablations from the sources | yes | several hours (one run: 15–40 min) | about $40–50 |

Run every command from the package root, after the install steps in [README.md](README.md).

## 0. Unpack the stored runs

Match files over 1 MB are stored gzipped. Unpack them once, keeping the `.gz` files:

```bash
find output -name '*.json.gz' -exec gunzip -k {} +
```

## Level 1: tables from the stored runs (no API calls)

```bash
python benchmark/evaluation_report.py summary     # per-run and per-case results
python benchmark/graded_score.py                  # graded option scores (related counts as half a match)
python benchmark/paper_stats.py                   # paired bootstrap, McNemar, Cliff's delta, detectable difference
```

The results are written to `output/evaluation/report/`, which also holds the stored copies to compare against.

| Paper table or claim | Source |
|---|---|
| Fidelity (DelveDSpace against the expert models; strict and graded) | `report/summary.md` (M1–M6, both views); `report/graded_score/graded_score.md` |
| Baselines (L1 long context, L5 prior knowledge) | `report/summary.md` (B1–B12; B10 is the run labelled S3) |
| Paired comparison against L1 (bootstrap CIs, McNemar, Cliff's δ) | `report/paper_stats/paper_stats.md` |
| Ablations (A1–A4) | `report/summary.md` (A1–A4); A4's last non-empty draft: `c2-rl-monitoring/rewrite_s42/last_draft/` |
| Stability across seeds and cost | `report/stability_<case>_full/stability.md`; tokens and time per run in `report/summary.md` and `runs.csv` |
| Size-matched comparison | `report/size_matched/size_matched.md` |
| Relevance-filter replay (C2) | `report/relevance_replay/` |
| Evidence check (do cited passages support the values?) | `report/evidence_check/` |
| Unmatched values that are valid knowledge outside the expert model (C1) | `report/unmatched_validity/` |
| Agreement of a second judge model | `report/judge_agreement/` |
| C3 (counts, scoreboard, stability, design points) | `report/summary.md` (M7–M9); `report/stability_c3-git-at-scale_full/`; the sample wiki in `examples/c3-git-at-scale/sample/` |

### Run identifiers

`output/evaluation/runs.csv` lists every run: row, case, variant, seed, status, tokens, time, and the paths of its
design space and match files. Each run folder holds:
- `config.yaml`, the exact configuration;
- the design space (`*_taxonomy_*.json`), with every iteration, the edit log, the Critic's feedback and the token counts;
- the matcher's results for both expert views (`match_selected/`, `match_final/`): every judged pair, the alignment and the metrics.

| Rows | Case | Variant | Seeds |
|---|---|---|---|
| M1–M3, M4–M6, M7–M9 | C1, C2, C3 | full workflow | 42, 43, 44 |
| B1–B3 / B7–B9 | C1 / C2 | L1: whole corpus in one prompt | 42, 43, 44 |
| B4–B6 / S3 (= B10), B11, B12 | C1 / C2 | L5: use case only, no corpus | 42, 43, 44 |
| A1 / A2 | C1 / C2 | no Critic feedback | 42 |
| A3 / A4 | C1 / C2 | whole-model rewriting instead of validated edits | 42 |
| S1, S2 | C3 sample | smoke runs, full and without feedback | 42 |

The stored runs exclude the passages, open codes and model transcripts, because they contain source text. Level 3
regenerates them.

## Level 2: LLM-judged checks on the stored runs

These scripts call the matcher's judge, or a second judge model. They need `OPENAI_API_KEY`.

```bash
python benchmark/evaluation_report.py stability --case c1-ml-workflow   # seeds matched to each other
python benchmark/size_matched.py                                        # DelveDSpace cut to the baseline's size, rematched
python benchmark/relevance_replay.py                                    # dimension selection with the relevance filter
python benchmark/evidence_check.py                                      # cited passages vs. values
python benchmark/unmatched_validity.py                                  # unmatched C1 values
python benchmark/judge_agreement.py --model openai/gpt-5.5              # second judge
```

Rescore one run against an expert model:

```bash
python main.py --match-gt output/evaluation/c1-ml-workflow/full_s42/<run>_taxonomy_<ts>.json \
               --gt benchmark/c1-ml-workflow/gt
```

The judge is an LLM, so labels can differ slightly between calls. The matcher's distance thresholds come from
the expert models alone (`python benchmark/frame_thresholds.py`).

## Level 3: rerun from the sources

1. Retrieve the sources and build the corpora. Source texts are not distributed; the manifests hold the SHA-256 of
   each file as retrieved for the paper. Some live pages have changed or disappeared since then (see the paper).

   ```bash
   python benchmark/fetch_sources.py                       # C1 and C2
   python benchmark/fetch_sources.py benchmark/c3-git-at-scale
   python benchmark/build_corpus.py                        # C1 and C2 passages
   python benchmark/build_corpus.py c3-git-at-scale
   ```

2. Run the matrix. Each row runs the workflow (or a baseline) with its configuration and seed, then scores it
   against both expert views:

   ```bash
   python benchmark/run_matrix.py --list                   # all rows
   python benchmark/run_matrix.py M1 --dry-run             # print the commands of one row
   python benchmark/run_matrix.py M1 M2 M3                 # run them
   ```

Models: `openai/gpt-5.6-luna` for generation and for the Critic, and `openai/gpt-5.4-mini` for the matcher's
judge (set in each configuration). A run on C1 takes about 40 minutes and 15M tokens. Inference is not
deterministic, so a rerun gives a different design space with similar scores (see the stability table).
