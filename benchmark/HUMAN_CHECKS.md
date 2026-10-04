# Human checks for the C1/C2 ground truth

These checks require human judgment and complete the ground-truth work (plan
`docs/plans/2026-10-03-1804-feat-ground-truth-conversion-and-matcher-plan.md`, R13 and R15). The
transcriptions, crosswalks and matcher are done and machine-validated. These checks confirm that they
represent the studies faithfully, and fix the use cases the scores rest on.

| # | Check | Who | Effort | Record in |
|---|---|---|---|---|
| 1 | C2 paper view and crosswalk | one author (ideally one who knows the C2 study) | ~45 min | `benchmark/c2-rl-monitoring/gt/README.md`, "Author check" table |
| 2 | C1 transcription | one author | ~45 min | `benchmark/c1-ml-workflow/gt/README.md`, "Author check" table |
| 3 | Use-case agreement | two authors | ~20 min | `benchmark/README.md`, "Evaluation frame", "Agreed by" line |
| 4 | Open evaluation decisions | the authors | ~15 min | `benchmark/README.md` and the paper plan, §8.7 |

## Rules for every check

- **Do not open any system output while checking.** That means DelveDSpace or baseline taxonomies,
  `*_gt_match.json`, `*_gt_metrics.json` and the HTML reports. The ground truth must not be shaped by what
  the system produced. If you have seen system outputs before, say so in the record (which ones, roughly
  when). That does not disqualify you, but it must be disclosed.
- **Write in the record table:** your name, the date, what you checked against, and every correction.
- **Corrections:** list them and leave the JSON files to the implementer. The files are regenerated or
  edited by script, so the validators and crosswalk checks rerun.
- **Changes after scores were seen:** any correction to a file that has already been scored must be logged
  under "Changes after scores were seen" in the evaluation-frame note. The C1 and C2 runs of 2026-10-02 have
  already been scored.

To browse the files: open `gt_paper.json` / `gt_model.json` in an editor. The crosswalk is a CSV; any
spreadsheet opens it.

---

## Check 1: C2 paper view and crosswalk

**Sources:**
- the paper: `papers/spaces/Architectural_Design_Decisions_for_Monitoring_Deployed_Reinforcement_Learning_Systems.pdf`
  (Table 2 and Fig. 2 on p. 8; §4 on pp. 9–12);
- the catalogue: `benchmark/c2-rl-monitoring/replication_package/memos/add-catalogue.md`.

**Files:**
- `benchmark/c2-rl-monitoring/gt/gt_paper.json`;
- `gt_crosswalk.csv`;
- `README.md`, where the "Discrepancies" section is numbered 1–7.

### Steps
1. **Decisions.** The paper view has the 7 decisions of Table 2 (`add1`–`add7`). Check each name and its
   short description against Table 2, Fig. 2 and §4. The descriptions paraphrase §4.
2. **Options per decision.** Check that the per-decision option counts in `gt_paper.json` equal Table 2: 3,
   16, 9, 6, 4, 9, 10 (57 in total).
   - Check the 37 options that the text names, in CamelCase bold italics on pp. 9–12. Each has a "named on
     p. N" reference in its `source` field; confirm a sample of about 10.
   - Confirm that each of the other 20 options (listed in the README) appears under the right decision in
     the catalogue.
3. **Decision links.** Check the 6 decision links against Fig. 2: the stereotypes and the label text.
4. **Crosswalk.** Check:
   - the 7 decisions and 57 options are `paper+model`;
   - the 6 ADD 6 options are `model only` (Hybrid Verifiers, Human Review, Model-based Verifiers Alone,
     Complex Scenario Testing, Simple Chat-based Monitoring, RLHF Alone);
   - there are no `paper only` elements.

### Decisions to make
The README discrepancy numbers are given in brackets.
- **[1] Action Failure Rate Monitoring.**
  - The paper puts it in ADD 2. The model declares it but links it to no decision.
  - **Decide:** keep it as an ADD 2 option in the paper view and unattached in the model view (current), or
    treat the missing link as a slip in the model and attach it to ADD 2 there as well.
- **[3] Second-decision placements stated on p. 12:**
  - KL Divergence from Reference Policy, "also a regularization technique in ADD 7";
  - Shadow Deployment, "also supports detection in ADD 6".
  - **Decide:** keep each option under its single decision (current), or add the second decision in the
    paper view.
- **[4] ADD 7's name.** Table 2 says "Reward Hacking Mitigation"; Fig. 2 and the model say "Reward Hacking
  Mitigation Architecture". **Decide** which name the paper view uses.
- **[2], [5], [6], [7]:** confirm the README's reading. These are the six model-only ADD 6 options, the
  paper's internal 53/57 option count, the decision type "unspecified", and the spelling differences.

### Done when
The "Author check" table in `benchmark/c2-rl-monitoring/gt/README.md` has your name, the date, "checked
against: paper Table 2, Fig. 2, §4, catalogue", every correction (or "none"), the decisions on [1], [3] and
[4], and your disclosure about system outputs.

---

## Check 2: C1 transcription

**Sources:** the paper, `papers/spaces/COMSI-2021-07-0084.R2_Warnett.pdf` (Table 2 on p. 5; the decision
sections on pp. 6–9; the scope statement on p. 2).

**Files:**
- `benchmark/c1-ml-workflow/gt/gt_paper.json`;
- `gt_crosswalk.csv`;
- `README.md`: its "Transcription rules" (numbered 1–8), "Discrepancies" and "Open issues" sections.

The paper view was already checked mechanically: all 43 options and 151 impacts match the PDF text of
Table 2. So this check is about the **rules and judgment calls**, not typos.

### Steps
1. **Rules.** Read transcription rules 1–8 and confirm each, or correct it.
   - The key ones:
     - rule 1: the paper view is exactly Table 2;
     - rule 3: practices named only in the text are not options;
     - rule 6: forces only from Table 2's legend.
   - Check that the 10 decisions and their options are the ADDs the paper presents (p. 2 says it describes
     a subset).
2. **Scope.** Confirm the model-only parts are those the paper says it omits (p. 2: deployment, CI/CD,
   MLOps, development environments), plus the parallelization, monitoring and model-adjustment decisions.
   These are the 18 `model only` decisions in the crosswalk.
3. **Spot check.** Pick 3 decisions and compare their options and force impacts (the `+`/`-` codes) in
   `gt_paper.json` with Table 2.

### Decisions to make (README "Open issues")
- **The 65 unattached model practices** (e.g. "Model registry", "Raw data store") are not options of any
  decision in the model. **Decide:** keep them out of scoring (current), or make some of them options of
  model-only decisions in the model view.
- **Decision types.** **Decide** whether to type the two "tasks" decisions (data-processing tasks,
  model-building tasks) as `multiple`, and the AutoML decision as described (whether to apply it, then
  where). Currently all are `unspecified`.
- **Table 2's ∅ rows.** **Decide** whether options of sub-decisions inherit the forces of their parent
  decision in the paper view. This doesn't affect current scoring.

### Done when
The "Author check" table in `benchmark/c1-ml-workflow/gt/README.md` has your name, the date, "checked
against: Table 2, pp. 2 and 6–9, transcription rules", the corrections (or "none"), the three decisions,
and your disclosure about system outputs.

---

## Check 3: use-case agreement (two authors)

Each study's use case (`taxonomy.use_case`) is the text DelveDSpace and every baseline receive. It must
come from the study's scope and research questions, never from the ground truth's content. Otherwise the
system is told the answer.

**Texts:**
- `examples/c1-ml-workflow/c1_ml_workflow_config.yaml`;
- `examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml`;

both as committed at `afebe10` and quoted in `benchmark/README.md`, "Evaluation frame".

### Steps (each author separately, then agree)
1. Compare each use case with the study's abstract and research questions (C1 p. 1; C2 pp. 1 and 3). Does
   it ask for the study's scope, no narrower and no broader?
2. **Leak check.** The use case must not name ground-truth decisions or options.
   - It may name the *phases* of the workflow or system the study covers (e.g. "data ingestion and
     processing", "monitoring infrastructure"), because those are the study's scope.
   - It must not name, for example, "CUSUM", "feature store", "circuit breaker" or "safe exploration".
   - Mark any phrase that reads like a decision or option.
3. Agree on the final text.
   - **If the text changes:** the change must be logged under "Changes after scores were seen", and the
     runs must be redone with the new text before any number is reported.

### Done when
The "Agreed by" line in the evaluation-frame note (`benchmark/README.md`) names both authors and the
date, and states "unchanged" or links the logged change.

---

## Check 4: open evaluation decisions

Decide these before numbers go into the paper, and record them in the evaluation-frame note. Any change
after scores were seen is logged there.

1. **"Related" rate.**
   - **Now:** the share of *system values* whose best label is `related`.
   - **Paper plan M7:** the share of *expert options* whose best edge is only `related`.
   - **Decide** which one the paper reports. Both are cheap to compute; one may be reported as secondary.
2. **The judge for reported numbers.**
   - All three LLM roles currently use `gpt-5.6-luna`, which also generated the runs. Its scores are not
     independent.
   - Judge sensitivity is large (C2 option F1 0.22 with `gpt-5.4-mini` vs. 0.43 with luna).
   - **Decide** the matching LLM for reported numbers (another model family if available). The human gold
     alignment (A6) will validate it.
3. **Human gold alignment (A6), to schedule next.**
   - Two authors label about 100 value–option pairs independently.
   - From those labels: κ between the two authors and between the authors and the judge, candidate recall,
     and calibration of the thresholds.
   - This is a separate task; a labeling sheet can be generated from the match files on request.
