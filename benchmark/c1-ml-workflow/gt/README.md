# C1 ground truth: ADDs for the machine learning workflow

Ground truth for case C1: Warnett & Zdun, *Architectural Design Decisions for the Machine Learning
Workflow*, IEEE Computer 55(3), 2022. The manuscript is `papers/spaces/COMSI-2021-07-0084.R2_Warnett.pdf`.
Format and validator: [`benchmark/gt_format.py`](../../gt_format.py).

| File | Content | Built by |
|---|---|---|
| `gt_model.json` | **Model view**: the authors' full CodeableModels model (`add_models/ml_adds.py`) | `python benchmark/parse_code_model.py --study c1` (static `ast` parse, no execution, no CodeableModels) |
| `gt_paper.json` | **Paper view**: Table 2 of the paper | transcription (below) |
| `gt_crosswalk.csv` | Status of every decision and option across both views | `python benchmark/gt_crosswalk.py build benchmark/c1-ml-workflow/gt` |

## Zenodo check (R8)

- **Record checked:** 10.5281/zenodo.5730291 (2026-10-03). It is the paper's reference [11]: "Architectural
  Design Decisions for the Machine Learning Workflow: Dataset and Code", Warnett & Zdun, 2021-11-29,
  Apache-2.0, one file, `ml_workflow_adds_v1.zip`.
- **Result:** **it contains a CodeableModels model of C1.** The package holds:
  - `add_models/ml_adds.py`, the model;
  - the coding memos (`sources_coding/`);
  - generated PlantUML views for 29 decisions (`_generated/ml_adds/`);
  - the LaTeX tables (`_generated/latex_files/`).

  So C1, like C2, has two views and a crosswalk.
- **Reproducing it:** the package is downloaded to `../replication_package/`, which is not committed
  (gitignored). Re-create it with:

  ```bash
  cd benchmark/c1-ml-workflow && mkdir -p replication_package && cd replication_package
  curl -sL -o pkg.zip "https://zenodo.org/records/5730291/files/ml_workflow_adds_v1.zip?download=1" && unzip -q pkg.zip && rm pkg.zip
  ```

- **No metamodel in the package:** it does not ship the CodeableModels guidance metamodel. Every stereotype it
  imports is defined in the copy shipped with C2 (`../../c2-rl-monitoring/replication_package/src/metamodels/guidance_metamodel.py`),
  so the parser uses that file.

## Counts

| | Model view | Paper view |
|---|---|---|
| Decisions | 28 (27 declared as decisions, plus 1 declared as a practice that has options) | 10 |
| Options | 186 declared, 121 linked to a decision | 43 |
| Forces | 104 | 30 (Table 2 legend f1–f30) |
| Option–force impacts | 737 | 151 |
| Decision links | 40 | not transcribed |
| Solution links (option → next decision, option dependencies) | 184 | – |
| Context links to domain classes | 25, skipped | – |

Crosswalk:

| | `paper+model` | `model only` | `paper only` |
|---|---|---|---|
| Decisions | 10 | 18 | 0 |
| Options | 43 | 143 | 0 |

**Model-only decisions:** the paper says it describes only "a subset of the ADDs that were modeled". It omits
"deployment, continuous integration and delivery, MLOps, and development environments" (p. 2). The 18
model-only decisions are those, plus the parallelization, monitoring and model-adjustment decisions:

- integrating an ML model;
- data storage;
- data-access interface;
- model serving;
- result availability;
- automatic integration and delivery, and delivery tasks;
- model versions in production;
- data versioning;
- environment provisioning;
- parallelizing data processing;
- parallelizing model building;
- monitoring the model in production;
- adjusting models from monitoring;
- CI/CD scope;
- pipeline testing;
- MLOps;
- development environment.

**Model-only options:**
- the options of those 18 decisions;
- 65 practices that are options of no decision. They appear only in dependency or next-decision links (e.g.
  "Model registry", "Raw data store", "Data ingestor"). They are recorded as `unattached` and excluded from
  scoring.

**Cross-check:** the model view matches the authors' 29 generated PlantUML views in every decision and option
link, except for the development-environment decision (discrepancy 1).

## Transcription rules (R9, written before transcribing)

1. **The paper view is Table 2 (p. 5).** The paper presents it as the overview of the ADDs, options, evidences
   and forces it describes; the text sections on pp. 6–9 discuss exactly these 10 decisions.
2. **Decision.** A Table 2 row group: a question with its options. The question is the decision's name, as
   in the model.
3. **Option.** A numbered entry under a decision in Table 2.
   - Practices named only in the text, such as "batch feature API", "event sourcing", "raw data store", "data
     ingestor" or "ML orchestrator", are not options of the paper view. The text names them as related
     practices or option variants, not as Table 2 options. They exist in the model view (mostly unattached).
   - The text's "considerations" are not options either.
4. **An option under several decisions** would keep one id with several `decision_ids`. None occurs in
   Table 2.
5. **Decision type.** `unspecified`: the paper states no type.
   - The "tasks" decisions (data processing tasks, model building tasks) read as multiple-choice, but the
     paper does not say so.
   - The AutoML decision is described as two parts (whether to apply AutoML, then which practices to
     automate), but Table 2 lists only "No AutoML" and "AutoML".
6. **Forces and impacts.** Only the forces in Table 2's legend (f1–f30), with the impacts Table 2 gives. Rows
   marked ∅ have no forces; the paper notes that sub-decisions share the forces of the prior decision.
7. **Descriptions.**
   - Decisions: none. The question is the description; the validator warns about the empty field.
   - Options: the paper describes options only in running prose, so their descriptions are the model's option
     text, the positional `option_name` (source `model_positional`). Where the model has none, the field is
     empty.
8. **Ids.** Elements present in the model reuse the model ids (decision variables, option and force name
   slugs). Paper-only elements would get `P`-prefixed ids; none occurs.

**How it was transcribed.**
- The package's `_generated/latex_files/overview_table.tex` is the same table as Table 2: same decisions,
  same options in the same order, same evidences and "#" column, with forces numbered differently. The paper
  view was read from it, and its force codes were mapped by name to Table 2's legend.
- Every option and impact was then compared with the paper's Table 2 as extracted by `pdftotext` (p. 5): all
  43 options and 151 impacts are identical, and all 30 legend names match model forces.
- Each element's `source` gives the Table 2 row (with its evidence sources) and, for decisions, the text
  section and page.

## Discrepancies

1. **"What development environment should be used?"** is declared with metaclass `practice` but has two
   options, "Use computational notebooks" and "Use an IDE". The model view treats it as a decision. The
   authors' generated view draws it as a practice, which accounts for the only cross-check differences. It is
   model-only (out of the paper's scope).
2. **Two elements named "Automated regression tests"** (`automated_regression_tests` and `experimentation`,
   lines 2057 and 2064) are a copy-paste slip in the model; their ids are their variable names. Both are
   unattached practices.
3. **A trailing space** in the model's "How to design the interface for data access? " is removed, as in the
   generated views.
4. **Force numbering:** Table 2 renumbers forces (f1–f30) relative to the package's generated tables (f1–f104).
   The views use names and ids, not codes.

## Open issues for the author check

- The 65 unattached model practices: should any count as options of a model-only decision for the model
  view? The parser follows the model's links strictly.
- Decision type of the two "tasks" decisions and of the AutoML decision (rule 5).
- Whether Table 2's ∅ rows should inherit their prior decision's forces in the paper view (rule 6). Not
  needed for scoring.

## Transcription and author check

- **Transcribed by:** Claude Code (implementer), 2026-10-03, following the rules above.
  - No description was written by an LLM. The option texts are the authors' model text.
  - No DelveDSpace or baseline output was open during transcription. The transcriber had, however, reviewed
    DelveDSpace C1 runs of 2026-10-02 earlier in the same session.
  - The paper view copies Table 2 row by row and was checked mechanically against the PDF text, which leaves
    no room for choosing wording.
- **Author check (R15):** *pending.*

  | Who | Date | Checked against | Corrections |
  |---|---|---|---|
  | | | paper Table 2 (p. 5), transcription rules, crosswalk | |

  To do: confirm the rules and the open issues, and record whether the checker had seen any system output.
