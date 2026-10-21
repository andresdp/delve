# Unmatched values: valid knowledge the expert model leaves out? (c1-ml-workflow; judge openai/gpt-5.4-mini)

Up to 40 unmatched candidate values per run (seed 0). Shares are of the judged sample; `valid_extra_est` = share × the run's unmatched values. Mean [min–max] over seeds.

| Method | Seeds | values | unmatched | judged | in_scope | genuine | covered_yes | covered_partly | evidence_ok | valid_extra | valid_extra_est |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Delve | 42 43 44 | 232 [198–276] | 107 [89–127] | 40 [40–40] | 0.97 [0.93–1.00] | 0.93 [0.93–0.95] | 0.01 [0.00–0.03] | 0.79 [0.78–0.82] | 0.99 [0.97–1.00] | 0.18 [0.17–0.20] | 20 [16–25] |
| L1 | 42 43 44 | 74 [67–80] | 19 [14–23] | 19 [14–23] | 1.00 [1.00–1.00] | 1.00 [1.00–1.00] | 0.01 [0.00–0.04] | 0.84 [0.79–0.87] | 1.00 [1.00–1.00] | 0.15 [0.09–0.21] | 3 [2–3] |

Judge failures (excluded, retried on rerun): 0.
