# C2 ground truth: monitoring deployed RL systems

Ground truth for case C2: Fang, Warnett & Zdun, *Architectural Design Decisions for Monitoring Deployed
Reinforcement Learning Systems* (2026) (`papers/spaces/`). Its replication package is Zenodo
10.5281/zenodo.20305497 (Apache-2.0), copied to `../replication_package/`. Format and validator:
[`benchmark/gt_format.py`](../../gt_format.py).

| File | Content | Built by |
|---|---|---|
| `gt_model.json` | **Model view**: the authors' full CodeableModels model (`src/model/model.py`) | `python benchmark/parse_code_model.py` (static `ast` parse, no execution, no CodeableModels) |
| `gt_paper.json` | **Paper view**: the design space as the paper reports it | transcription (below) |
| `gt_crosswalk.csv` | Status of every decision and option across both views (`paper+model`, `model only`, `paper only`) | `python benchmark/gt_crosswalk.py build benchmark/c2-rl-monitoring/gt` |

Check: `python benchmark/gt_format.py benchmark/c2-rl-monitoring/gt/gt_*.json` and
`python benchmark/gt_crosswalk.py check benchmark/c2-rl-monitoring/gt`.

## Counts

| | Model view | Paper view | Paper's own numbers |
|---|---|---|---|
| Decisions (ADDs) | 7 | 7 | 7 (Table 2, abstract) |
| Options | 63 declared, 62 linked to a decision | 57 | 57 (Table 2 sums, abstract, §5.1); 53 on p. 7 |
| Forces | 43 | not transcribed | 72 decision drivers (Table 2, abstract); 59 on p. 7 |
| Per-decision force texts | 72 (memo driver rows) | – | 72 = sum of Table 2 driver counts |
| Option–force impacts | 150 | – | – |
| Decision links | 6 (Fig. 2) | 6 (Fig. 2) | – |

Crosswalk: 7 decisions `paper+model`; 57 options `paper+model`, 6 `model only`; no `paper only`.

The model view matches the authors' generated PlantUML view (`_generated/rl_monitoring_adds/all_view_with_forces.txt`)
exactly: same 7 decisions, 63 options, 43 forces, 62 option links and 150 impacts, with no differences.

## Sources per element

**Model view** (`parse_code_model.py`):

| Element | Source |
|---|---|
| Decisions, options, forces | the `CClass` declarations in `model.py` (line in each element's `source`) |
| Decision name and question | Name from the model. Question and the "Key trade-off" description come from the ADD's section in `memos/add-catalogue.md` |
| Option description | Normally the `description` tagged value of the option link. Three options pass their text positionally (`option_name`) and are marked `model_positional`: Ensemble Reward Model Agreement, Deployment-Time Feedback Loop Simulation, Reward Model vs Outcome Divergence. Fallback: the memo |
| Per-decision force text | the "Decision Drivers" table of each ADD in the memo. Forces have no description of their own because the memo describes each force differently under each decision |
| Impacts and links | `add_force_relations` and `add_links` calls. Stereotypes are resolved through `src/metamodels/guidance_metamodel.py` |

Ids:
- decisions: the model variables (`add1`…`add7`);
- options and forces: slugs of the class names (e.g. `bootstrap_far_bfar`, `detection_latency`).

**Paper view**: the paper's tables, figure and text.
- **Decisions:** from Table 2 and Fig. 2 (p. 8). Their descriptions follow the wording of §4 (pp. 8–11).
- **Options:** the paper gives each decision's option count (Table 2) and names most options in §4 (pp. 9–12).
  For the full catalog it points to its replication package [8]. Each decision's option list and its
  descriptions come from that catalogue (`memos/add-catalogue.md`), whose option counts per decision equal
  Table 2.
- **Option sources:** each option's `source` gives the pages where the text names it. The following 20
  options are counted in Table 2 but not named in the text:
  - A/B Policy Comparison, Metric Divergence Monitoring, Context-Sliced Signal Monitoring, Latency SLO
    Monitoring, Security-Significant Signals;
  - Policy Rollback, Rollback with Learning-Rate Stabilisation, Blue-Green Traffic Shift, Graceful
    Degradation, Continuous Adaptation, Mid-Run Reward Function Update;
  - Naive Simple Mean, CUSUM Sequential Test, Hotelling Multivariate Test, Embedding-Based Drift Detection,
    PSI / KL Input Distribution Test;
  - Fixed Statistical Threshold, Variance-Tuned Threshold, Reward Model vs Outcome Divergence, SFT on
    Non-Gaming Data.
- **Decision links:** from Fig. 2. The paper view doesn't transcribe forces; they are in the model view.

## Discrepancies

1. **Action Failure Rate Monitoring**:
   - The paper places it in ADD 2: it is named on p. 10 and counted among Table 2's 16.
   - The model declares it, with forces CatastrophicDegradation and SLOBreachDetection, but links it to no
     decision.
   - The model view records it as `unattached`, so it is excluded from model-view scoring. It is scored in
     the paper view.
2. **Six ADD 6 options exist only in the model** (`model only`): Hybrid Verifiers, Human Review, Model-based
   Verifiers Alone, Complex Scenario Testing, Simple Chat-based Monitoring, RLHF Alone.
   - They are linked to ADD 6 and have forces.
   - They are missing from the catalogue memo and from Table 2's count of 9.
3. **Options the paper places under a second decision** (§5.1 RQ2, p. 12):
   - KL Divergence from Reference Policy "appears as a monitoring signal in ADD 2 and as a regularization
     technique in ADD 7". ADD 7 lists that as the separate option Regularisation to Reference Policy.
   - Shadow Deployment "appears as a response option in ADD 3 and as an evaluation mechanism supporting
     detection in ADD 6". It is not among ADD 6's options in the catalogue or the model.

   Both stay under their single decision in both views; this choice is an open issue for the author check.
4. **ADD 7's name**: Table 2 says "Reward Hacking Mitigation"; Fig. 2 and the model say "Reward Hacking
   Mitigation Architecture". Both views use the latter.
5. **The paper's internal counts**: p. 7 reports "53 decision options, and 59 decision drivers". The abstract,
   Table 2 and §5.1 report 57 and 72. The views follow the latter, which the catalogue confirms.
6. **Decision type**: no decision carries the metamodel's "Single Answers" or "Multiple Answers" stereotype,
   and the paper states no type. All seven are `unspecified`.
7. **Spelling**: the paper's text writes some names differently from the model (e.g.
   *ConstrainedPolicyOptimization* vs. "Constrained Policy Optimisation"; *DecoupledApproval* vs. "Decoupled
   Approval / Feedback"). Both views use the model's names.

## Transcription and author check

- **Transcribed by:** Claude Code (implementer), 2026-10-03. The decision descriptions and the option page
  references were transcribed from the paper; the option lists and descriptions come from the catalogue memo.
  No description was written by an LLM: every one is the authors' text, from the model, the memo or the paper.
- **System outputs seen:** no DelveDSpace or baseline output was open during transcription. The
  transcriber had, however, reviewed the DelveDSpace C2 runs of 2026-10-02 earlier in the same session. The
  transcription copies decisions and options as the paper and catalogue list them and leaves no room for
  choosing wording. The only judgment calls are listed in the discrepancies above (items 1, 3 and 4).
- **Author check (R15):** *pending.* Steps and decisions: [HUMAN_CHECKS.md](../../HUMAN_CHECKS.md),
  check 1.

  | Who | Date | Checked against | Corrections |
  |---|---|---|---|
  | | | paper (Table 2, Fig. 2, §4) and the crosswalk | |

  To do: confirm discrepancies 1–4 (in particular, whether the two second-decision placements of item 3
  should enter the paper view), and record whether the checker had seen any system output.
