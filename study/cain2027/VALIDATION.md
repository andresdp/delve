# Validating the agent designs

There is no ground truth for the briefs: no study defines the correct architecture for these four systems, and
a brief admits several good designs. The ADR sets are validated in three layers. Only the third needs human
judgment.

## Layer 1: the expert model as a per-brief reference

The C1 expert model (`inputs/gt_model.json`, Warnett and Zdun) is used as a yardstick, not as the answer.
For each brief, `reference.py` derives from the brief's hidden forces (`briefs.yaml`) and the expert impact
ratings:

- **Relevant decisions:** the expert decisions whose options differ in their summed impact on the brief's forces.
  A good design for the brief should address them.
- **Preferred options:** for each relevant decision, the options with the best summed impact.

`reference.py` writes them to `references/<brief>.md` (readable, for review) and `references/references.json`
(with the hashes of the briefs and the model); run it once the briefs are final and before any session runs.
`score.py` computes the same reference (`score.relevant_decisions`).

| Metric | Definition | Source |
|---|---|---|
| Decision coverage | Expert decisions with at least one matched alternative, over all 28. Each alternative counts through its best match only (a "same" label first, then the smallest embedding distance), so one broad alternative cannot claim many decisions. Reported with two variants: `_same` (only matches labelled "same") and `_lenient` (every same, broader or narrower match) | Matcher |
| Relevant-decision coverage | Relevant decisions of the brief with at least one matched alternative, over all relevant decisions (same three readings) | Matcher and reference |
| Requirements fit | On the best matches: per touched expert decision, (chosen - worst) / (best - worst) of the summed impacts on the brief's forces; ties excluded; a choice matching no option of that decision is counted as unmatched; mean over qualifying decisions, always reported with their number (`fit_decisions`) | Matcher and impacts |
| Driver recall | Share of the brief's forces that the ADRs' stated drivers name | Matcher (drivers against force names) |

Caveats to report:

- The expert model reflects one study's judgment, and its impact ratings were not made for these briefs.
- Condition E sees the expert decisions and options (not the impacts), so it is favoured on coverage and fit: it
  is "full expert-model access", not a competitor.
- Matching agent wording to expert options uses an LLM judge (`openai/gpt-5.4-mini`, frozen thresholds). The
  pilot showed it lenient: it labels loosely related options "same" (for example, an online feature-serving
  pipeline and a CI/CD pipeline), so a broad alternative matched up to 14 expert options. Hence the best-match
  reading as the primary one, with the lenient one reported to show the gap. The best matches are checked by hand
  (`score.py --export-labels`), and the share judged correct is reported as the matcher's precision and recorded
  in the evaluation frame (`benchmark/README.md`).

## Layer 2: checks without a reference

| Check | Definition | Conditions |
|---|---|---|
| Structure | The output schema holds; the chosen option is one of those considered | All |
| Grounding | Share of choices with a citation; share of citations that exist in the condition's graph | M, E |
| Consistency | `ddspace point` warnings on the chosen value ids (rejected values, two values of one dimension), and ids that do not exist | M, E |
| Exploration | Alternatives per decision; design points explored with `ddspace point` | All; points M, E |
| Cost | Input and output tokens, priced from `rates.yaml` | All |
| Network use | Sessions with network commands other than `ddspace` are flagged and reported | All |

## Layer 3: a small blind human rating

- **Sample:** repetition 1 of every brief and condition (4 briefs x 3 conditions = 12 ADR sets).
- **Blinding:** `rating.py packets` renders each set as one packet (the brief, then the ADRs) under a random
  code, without value ids, citations, and any M or E graph id found in the text (with `--workspaces`). Each rater
  gets a sheet with the packets in a different random order. The key (`results/rating-key/key.json`) is kept
  apart, and the raters do not open it before rating. Packets whose wording still mentions the design space are
  listed for a check.
- **Raters:** two authors, independently.
- **Rubric** (each item 1 to 4: 1 = poor, 2 = weak, 3 = adequate, 4 = good):
  1. **Coverage:** the ADRs address the decisions this system needs.
  2. **Trade-offs:** the options and their pros and cons are sound and relevant.
  3. **Fit:** the choices and rationale follow from the brief's requirements.
  4. **Correctness:** nothing is wrong or misleading.
- **Agreement:** `rating.py agreement` computes the quadratic-weighted Cohen's kappa per item and lists the
  disagreements of two or more points. These are discussed and resolved (`sheet-resolved.csv`), and both the raw
  and the resolved scores are reported (`rating.py agreement --unblind`, per condition).

Wording can still reveal the condition (for example, labels copied from the expert model); report this as a
limit of the blinding.

## Qualitative illustration

For one brief, the three ADR sets (`results/adrs/<session>/`) are compared side by side: which decisions and
options each condition reached, and where the design space changed the choice.

## Repetitions and the trade-off variant (v2)

Added after the first 24 sessions (2026-10-26), and reported as such:

- **Five repetitions** per brief and condition instead of two (60 sessions per prompt variant), for ranges that
  can be read. The first 24 sessions are kept; the runs only add repetitions 3 to 5.
- **Fit basis.** In v1, fit rested on few decisions (about two per session in N and M), because many choices
  matched no expert option of the decision they touched. Fit is reported with `fit_decisions`, and the
  human rating's fit item is the main evidence on fit.
- **Prompt v2** (`prompt-v2.md`): v1 plus an explicit trade-off step (rank the brief's requirements, state pros
  and cons per driver, name the deciding driver). It is the same for all three conditions, runs with the same
  model, workspaces and briefs, and writes to `results-v2/`. It was declared after seeing v1's low fit, so it is
  an exploratory variant: v1 stays the primary result, and v2 is reported next to it, never instead of it.

## What the paper reports

- Per condition, means and ranges of the layer 1 and layer 2 metrics, also per brief (only four briefs); fit
  with its number of decisions; v1 as the primary result, v2 as the exploratory variant.
- The layer 3 ratings with their agreement.
- One qualitative example.
- Threats: one domain, four author-written briefs, author-chosen forces, the expert model as the only reference, a
  single agent and model from one provider (also the judge's), five repetitions, and a variant (v2) chosen after
  seeing v1's results.
