# Seed stability: c3-git-at-scale full (selected view)

Each pair: the second run scored against the first, used as the reference, with the ground-truth matcher (mode judge). Mean option F1 0.77; mean decision F1 0.83 strict, 0.96 lenient.

| Pair | Ref. values | Other values | Option P | Option R | Option F1 | Decision F1 strict | Decision F1 lenient |
|---|---|---|---|---|---|---|---|
| 42 vs 43 | 128 | 124 | 0.77 | 0.76 | 0.77 | 0.86 | 0.98 |
| 42 vs 44 | 128 | 157 | 0.73 | 0.84 | 0.78 | 0.74 | 0.91 |
| 43 vs 44 | 124 | 157 | 0.72 | 0.84 | 0.77 | 0.89 | 1 |
| mean |  |  | 0.74 | 0.81 | 0.77 | 0.83 | 0.96 |
