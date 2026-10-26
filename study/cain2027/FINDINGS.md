# Findings of the C1 agent study

Results of the study as run on 2026-10-26, with what they support and what they do not. The procedure is in
`RUNNING.md` and the validation criteria in `VALIDATION.md`. Numbers come from `results/scores.json` (v1) and
`results-v2/scores.json` (v2).

## What was run

- **Task:** a coding agent (Codex CLI, model `gpt-6-luna`) writes concise Architecture Decision Records (ADRs)
  for four ML-enabled systems described in short briefs: `fraud`, `vision`, `forecast`, `documents`.
- **Conditions:** N (the brief only), M (the design space mined from the C1 sources, seed 42), E (the C1 expert
  decision model as a design space, with forces and impacts held out).
- **Sessions:** 4 briefs x 3 conditions x 5 repetitions = 60 sessions per prompt variant.
  - v1 (`prompt.md`): the primary result.
  - v2 (`prompt-v2.md`): an explicit trade-off step, added after seeing v1's results; exploratory.
- **Execution:** all 120 sessions succeeded, with no network commands or web search. In M and E, every session
  checked at least two design points with `ddspace point` (a required step of the agent guide).
- **Scoring:** the agent's options were matched to the expert options by the ground-truth matcher (judge
  `openai/gpt-5.4-mini`, frozen settings), each option through its best match only.
- **Cost:** $0.29 (v1) and $0.26 (v2) for the sessions; about 1 minute per session in M and E, 25 s in N.

## Results (v1)

Mean ± standard deviation over 20 sessions per condition. p: two-sided Mann-Whitney U over sessions. Sessions
of one brief are not independent, so the p-values are indicative.

| Metric | N | M | E | p (N vs M) | p (M vs E) |
|---|---|---|---|---|---|
| ADRs written | 4.05 ± 0.76 | 5.25 ± 1.41 | 6.85 ± 1.79 | | |
| **Relevant-decision coverage** (best match) | **0.10 ± 0.06** | **0.22 ± 0.12** | **0.34 ± 0.08** | 0.001 | < 0.001 |
| Relevant-decision coverage, lenient | 0.16 | 0.32 | 0.55 | | |
| Decision coverage (all 28 expert decisions) | 0.09 | 0.17 | 0.27 | | |
| Requirements fit | 0.84 ± 0.29 | 0.62 ± 0.21 | 0.87 ± 0.11 | 0.009 | 0.001 |
| Decisions fit rests on (`fit_decisions`) | 0.90 | 1.75 | 4.55 | | |
| Choices matching no option of the decision they touch | 0.95 | 2.10 | 0.70 | | |
| Driver recall (brief's hidden forces named as drivers) | 0.49 ± 0.17 | 0.50 ± 0.20 | 0.66 ± 0.20 | 0.849 | 0.024 |
| Alternatives matching an expert option | 0.42 | 0.64 | 0.99 | | |
| Decisions listed as not covered (`uncovered`) | 6.2 | 4.6 | 5.0 | | |
| Choices with a citation | - | 0.98 | 1.00 | | |
| Citations that exist in the space | - | 1.00 | 1.00 | | |
| Citations on the choice that refer to the chosen value | - | 0.96 | 0.97 | | |
| Passage citations whose source adopts the chosen value | - | 0.96 | - | | |
| Citations whose source rejects the chosen value | - | 0 | 0 | | |
| `ddspace point` warnings on the chosen values | - | 0.45 | 0 | | |
| Design points checked | - | 2.40 | 2.25 | | |

Relevant-decision coverage per brief (N / M / E):

| Brief | N | M | E |
|---|---|---|---|
| documents | 0.09 | 0.22 | 0.40 |
| forecast | 0.14 | 0.31 | 0.37 |
| fraud | 0.11 | 0.21 | 0.26 |
| vision | 0.06 | 0.16 | 0.34 |

## Findings

### 1. The design space widens what the agent considers (robust)

Relevant-decision coverage doubles from N to M and triples from N to E, in every brief and under every
reading of the matcher (best match, same-only, lenient). With a design space, the agent writes more ADRs and
leaves fewer needed decisions open. This is the main quantitative result.

### 2. With the design space, choices are traceable and backed by evidence

In M, 98% of the choices cite the space, every citation exists, and 96% of the passage citations on a chosen
option are evidence for that exact value from a source that adopts it. No citation comes from a source that
rejects the chosen value. In E, 97% of the citations refer to the chosen value or its dimension. In N, a
choice rests on the model's own knowledge and cannot be audited.

Limits of this claim:

- This is grounding, not quality: a cited choice is justified and traceable, not necessarily better (finding 3).
- N has nothing to cite, so grounding is a property of M and E, not a measured difference with N.
- The blind rating cannot see grounding (citations are removed from the packets to hide the condition), so the
  claim rests on these automated checks.

### 3. The mined space does not steer choices toward the expert preferences (fit)

Requirements fit is lower in M (0.62) than in N (0.84) and E (0.87). Three things qualify this:

- **Small basis.** In N and M, fit rests on 1 to 2 decisions per session. Many choices are worded in the mined
  space's vocabulary and match no expert option of the decision they touch. Only E has a solid fit estimate.
- **Concentrated.** Most of M's low fit comes from one decision, how to serve predictions. In all five
  `documents` sessions and two `forecast` sessions, M chose scheduled batch prediction, which the expert
  reference ranks worst for those briefs' forces (it prefers microservice serving).
- **Defensible choices.** Batch prediction is a reasonable design for weekly demand forecasts and for
  classifying millions of documents a day. The expert impacts were rated in general, not for these briefs, so
  fit measures agreement with generic impact ratings rather than design quality.

Interpretation: the mined space records options and who adopts them, not their trade-offs (how an option
affects latency, cost or reproducibility). The agent's evidence is adoption evidence, so it does not tell the
agent which option suits the brief's priorities. Only the expert model has impact ratings, and they are held
out even from E.

### 4. Asking for explicit trade-offs does not change this (v2)

| Metric (v2) | N | M | E |
|---|---|---|---|
| Relevant-decision coverage | 0.09 | 0.21 | 0.28 |
| Requirements fit | 0.77 | 0.66 | 0.85 |
| Driver recall | 0.56 | 0.55 | 0.64 |
| Design points checked | - | 3.20 | 2.15 |
| Passage citations whose source adopts the chosen value | - | 0.98 | - |

The trade-off step left coverage and fit essentially unchanged (M's fit 0.62 to 0.66; the N vs M fit difference
is no longer significant, p = 0.14, because N dropped). Driver recall rose slightly in N and M, and M checked
more design points. This supports finding 3: the limit lies in the design space's content (no trade-off
knowledge), not in how the agent is asked to reason.

### 5. Process observations

- **Design points are used as instructed, not explored.** Before the guide required it, no session ran
  `ddspace point`. Since then, most sessions run exactly the two required checks.
- **E is an upper bound, not a competitor.** E sees the expert options' names: 99% of its alternatives match an
  expert option. Its coverage advantage over M is partly built in.
- **The judge is lenient.** It labels loosely related options "same" (for example, an online feature-serving
  pipeline and a CI/CD pipeline). The lenient reading inflates coverage (M's relevant coverage: 0.22 best match,
  0.32 lenient); the best-match reading is the one reported.

## Reporting decisions

- **Main story:** findings 1 to 3. Coverage and grounding as the contribution; fit as the honest limit,
  reported with its decision counts and the batch-serving example.
- **v2:** one sentence in the discussion or threats (finding 4), not part of the main story; its results stay
  in the artifact.
- **Qualitative example:** the `documents` brief across N, M and E (`results/adrs/documents-*-r1/`). It shows
  both the wider coverage and the well-cited batch-serving choice that fit penalizes.
- **Future work** suggested by the results: mine forces and impacts (trade-offs) along with options.

## Still pending

- **Label check** (matcher precision): mark the best matches of repetition 1 of each brief and condition (12
  label files; `score.py --export-labels` first). Report the share judged correct.
- **Blind rating** (layer 3): the main evidence on choice quality, since fit is weak. See `RUNNING.md` step 8.

## Threats

One domain (C1, ML workflow); four author-written briefs with author-chosen forces; the expert model as the
only reference, with impacts not rated for these briefs; one agent and model from one provider, which also
provides the judge; five repetitions; a lenient LLM judge (precision pending); v2 chosen after seeing v1's
results; and changes made after the pilot (the required point check, best-match scoring), both recorded in the
commit history.
