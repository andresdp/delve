# Statistics for the paper

Strict option scores, selected view. Over seeds: mean ± sd. Paired: over expert options (10,000 bootstrap resamples). 3 seeds per system: δ and McNemar are descriptive.

## c1-ml-workflow, paper view (43 expert options)

| System | Seeds | Option P | Option R | Option F1 | Decision F1 lenient |
|---|---|---|---|---|---|
| Delve | 3 | 0.36 ± 0.04 | 0.81 ± 0.02 | 0.50 ± 0.04 | 0.87 ± 0.09 |
| L1 | 3 | 0.62 ± 0.08 | 0.67 ± 0.03 | 0.64 ± 0.03 | 0.90 ± 0.04 |
| L5 | 3 | 0.50 ± 0.05 | 0.47 ± 0.03 | 0.48 ± 0.03 | 0.76 ± 0.06 |

Minimum detectable recall difference (n = 43, pooled recall 0.65): about ±0.20.

| Delve vs | Δ option F1 (means) | Cliff's δ (F1, seeds) | Δ recall, paired over options [95% CI] | McNemar, seed 42 (Delve only / other only, p) |
|---|---|---|---|---|
| L1 | -0.14 | -1.00 | +0.15 [+0.07, +0.23] | 8 / 2, p = 0.109 |
| L5 | +0.01 | +0.33 | +0.34 [+0.23, +0.45] | 18 / 3, p = 0.002 |

## c1-ml-workflow, model view (121 expert options)

| System | Seeds | Option P | Option R | Option F1 | Decision F1 lenient |
|---|---|---|---|---|---|
| Delve | 3 | 0.54 ± 0.01 | 0.71 ± 0.05 | 0.61 ± 0.01 | 0.90 ± 0.02 |
| L1 | 3 | 0.74 ± 0.05 | 0.61 ± 0.02 | 0.67 ± 0.03 | 0.92 ± 0.05 |
| L5 | 3 | 0.63 ± 0.07 | 0.44 ± 0.04 | 0.52 ± 0.05 | 0.78 ± 0.02 |

Minimum detectable recall difference (n = 121, pooled recall 0.59): about ±0.12.

| Delve vs | Δ option F1 (means) | Cliff's δ (F1, seeds) | Δ recall, paired over options [95% CI] | McNemar, seed 42 (Delve only / other only, p) |
|---|---|---|---|---|
| L1 | -0.06 | -1.00 | +0.10 [+0.03, +0.16] | 28 / 10, p = 0.005 |
| L5 | +0.09 | +1.00 | +0.27 [+0.20, +0.34] | 43 / 8, p = 0.000 |

## c2-rl-monitoring, paper view (57 expert options)

| System | Seeds | Option P | Option R | Option F1 | Decision F1 lenient |
|---|---|---|---|---|---|
| Delve | 3 | 0.25 ± 0.02 | 0.53 ± 0.04 | 0.34 ± 0.03 | 0.57 ± 0.08 |
| L1 | 3 | 0.55 ± 0.00 | 0.46 ± 0.06 | 0.50 ± 0.04 | 0.69 ± 0.06 |
| L5 | 3 | 0.26 ± 0.03 | 0.28 ± 0.14 | 0.26 ± 0.05 | 0.51 ± 0.07 |

Minimum detectable recall difference (n = 57, pooled recall 0.42): about ±0.18.

| Delve vs | Δ option F1 (means) | Cliff's δ (F1, seeds) | Δ recall, paired over options [95% CI] | McNemar, seed 42 (Delve only / other only, p) |
|---|---|---|---|---|
| L1 | -0.16 | -1.00 | +0.07 [-0.07, +0.20] | 19 / 9, p = 0.087 |
| L5 | +0.08 | +0.78 | +0.25 [+0.12, +0.38] | 27 / 4, p = 0.000 |

## c2-rl-monitoring, model view (62 expert options)

| System | Seeds | Option P | Option R | Option F1 | Decision F1 lenient |
|---|---|---|---|---|---|
| Delve | 3 | 0.27 ± 0.02 | 0.55 ± 0.06 | 0.36 ± 0.03 | 0.60 ± 0.09 |
| L1 | 3 | 0.56 ± 0.01 | 0.48 ± 0.08 | 0.51 ± 0.04 | 0.74 ± 0.05 |
| L5 | 3 | 0.27 ± 0.03 | 0.26 ± 0.14 | 0.25 ± 0.06 | 0.52 ± 0.06 |

Minimum detectable recall difference (n = 62, pooled recall 0.43): about ±0.17.

| Delve vs | Δ option F1 (means) | Cliff's δ (F1, seeds) | Δ recall, paired over options [95% CI] | McNemar, seed 42 (Delve only / other only, p) |
|---|---|---|---|---|
| L1 | -0.15 | -1.00 | +0.07 [-0.06, +0.20] | 21 / 10, p = 0.071 |
| L5 | +0.11 | +1.00 | +0.28 [+0.17, +0.40] | 30 / 4, p = 0.000 |

## Ablations (one seed; against the seed-42 full run and the full system's seed range)

| Case | Ablation | Option F1 paper / model | Recall paper | Decision F1 lenient paper / model | Full seed 42 F1 | Full seed range F1 |
|---|---|---|---|---|---|---|
| c1-ml-workflow | A1 nofeedback | 0.44 / 0.57 | 0.70 | 0.90 / 0.90 | 0.46 / 0.62 | 0.46–0.54 / 0.60–0.62 |
| c1-ml-workflow | A3 rewrite | 0.43 / 0.54 | 0.60 | 0.95 / 0.88 | 0.46 / 0.62 | 0.46–0.54 / 0.60–0.62 |
| c2-rl-monitoring | A2 nofeedback | 0.31 / 0.32 | 0.56 | 0.63 / 0.59 | 0.36 / 0.37 | 0.31–0.36 / 0.33–0.38 |

A4 (C2 rewrite) ended with an empty space and has no match; its last non-empty draft is scored separately (record §3.11).
