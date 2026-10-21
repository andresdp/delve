# Second-judge agreement: gpt-5.4-mini (judge 1) vs openai/gpt-5.5 (judge 2)

Same items, prompts and schemas. Agreement shows stability across judges, not correctness.

## Agreement

| Check | Question | Items | Raw agreement | Cohen's κ |
|---|---|---|---|---|
| Citations | supported/partial/unsupported | 1301 | 0.74 | 0.54 |
| Unmatched (C1) | in_scope | 177 | 0.98 | 0.49 |
| Unmatched (C1) | genuine_option | 177 | 0.94 | 0.45 |
| Unmatched (C1) | covered_by_expert | 177 | 0.72 | 0.38 |
| Unmatched (C1) | evidence | 177 | 0.86 | 0.50 |
| Unmatched (C1) | valid extra (derived) | 177 | 0.77 | 0.42 |

## Do the conclusions hold?

Citations: share supported (and values with ≥1 supported citation)

| Case | Method | Judge 1 | Judge 2 |
|---|---|---|---|
| c1-ml-workflow | Delve | 0.49 (0.82) | 0.52 (0.87) |
| c1-ml-workflow | L1 | 0.78 (0.97) | 0.83 (0.99) |
| c2-rl-monitoring | Delve | 0.40 (0.74) | 0.45 (0.79) |
| c2-rl-monitoring | L1 | 0.51 (0.80) | 0.62 (0.90) |

Unmatched C1 values: share that are valid extras (and covered partly)

| Method | Items | Judge 1 | Judge 2 |
|---|---|---|---|
| Delve | 120 | 0.18 (0.79) | 0.37 (0.57) |
| L1 | 57 | 0.14 (0.84) | 0.30 (0.65) |

Judge 2 calls this run: 1478 (≈1.28M input tokens, estimated from prompt length; output not counted).
