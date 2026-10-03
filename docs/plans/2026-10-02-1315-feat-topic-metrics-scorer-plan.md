---
title: Topic-Model Metrics Scorer (coherence and diversity at two levels) - Plan
type: feat
date: 2026-10-02
execution: code
status: proposed — not implemented; decisions recorded 2026-10-02 (§8)
related: >-
  docs/paper/SANER2027_PAPER_PLAN.md §5.1b (other fidelity measures), §8.4 (baselines L1–L3),
  CONCEPTS.md (Evidence Linking, Selected Dimensions, Scoreboard)
---

# Topic-Model Metrics Scorer - Plan

## Goal Capsule

- **Objective:** Score a design space (dimensions and values) with the metrics used in topic
  modeling (coherence and diversity), at both levels and across them, so that Delve and the
  topic-model baselines (BERTopic, TnT-LLM-style, long-context LLM) are described with the same,
  familiar numbers.
- **Scope:** Post-hoc scoring only. The scorer reads saved run artifacts; it is not a graph node,
  never routes the pipeline and never feeds back into generation (same contract as Observe-Only
  Evaluation).
- **Not a fidelity measure:** fidelity to the ground truth is measured by the matching protocol
  (paper plan §5.1). These metrics describe how lexically/semantically tight and distinct the
  groups are; they are reported as secondary, descriptive measures.
- **Stop conditions:** if computing a metric would require changing the pipeline's outputs beyond
  what §3.3 lists, stop and report.

---

## 1. Discussion: do coherence and diversity apply to a design space?

### 1.1 What the metrics measure in topic modeling

- **Topic coherence** scores a topic's top-N words by how much they co-occur in a reference
  corpus. Common variants: NPMI (normalized pointwise mutual information over document
  co-occurrence), C_V (sliding-window NPMI vectors compared by cosine; the default in many
  studies), UMass. Higher = the words "belong together".
- **Topic diversity** (TD, Dieng et al. 2020) is the share of unique words among all topics' top-N
  words. Higher = topics are less redundant. Inverted RBO (IRBO) is a rank-aware alternative.
- Both need a **word distribution per topic**, which topic models produce and Delve does not.

### 1.2 How they can apply to Delve

Delve's groups are not word distributions, but they are **groups of documents**:

- **Labeling** assigns each passage to one dimension and one value (single-label).
- **Evidence linking** records, per value, the passages whose open codes support it
  (`supporting_doc_ids`, possibly several values per passage).

From a group's documents we can derive its top words with **class-based TF-IDF** (c-TF-IDF, the
procedure BERTopic uses to describe its own topics) and then compute the standard metrics. The same
procedure applies to any method that outputs groups of documents, which is what makes the metrics
comparable across Delve and the baselines.

Delve has **two levels** (dimension ⊃ values), so the metrics apply at each level, and the
hierarchical-topic-model literature adds metrics **across** levels:

| Level | Group | Coherence | Diversity |
|---|---|---|---|
| Dimension | passages of the dimension | coherence of its top words | TD across dimensions |
| Value | passages supporting the value | coherence of its top words | TD across all values; TD among siblings |
| Across | dimension and its values | parent–child coherence | parent–child diversity, parent–non-child diversity |

The cross-level metrics follow hierarchical topic model evaluation (e.g. Wu et al., AAAI 2024,
"On the Affinity, Rationality, and Diversity of Hierarchical Topic Modeling", which uses
parent–child coherence, parent–child diversity, sibling diversity and parent–non-child diversity).
*Verify the exact definitions and citation before writing the paper.*

### 1.3 Does it make sense? Yes, with caveats

1. **Lexical vs. conceptual groups.** A decision point groups *alternatives to one question*
   (e.g. *Drift Detection Test*: CUSUM, KS test, covariance-weighted test). Its passages can be
   conceptually tight but lexically varied, while a topic built around frequent words
   ("model", "data", "pipeline") scores high. Word-based coherence is known to correlate weakly
   with human judgments (Hoyle et al., NeurIPS 2021, "Is Automated Topic Model Evaluation
   Broken?"). Mitigation: also report **embedding-based** coherence and separation (§2.4), and a
   **shuffled baseline** (§2.5) so every number has a reference point.
2. **Small value groups.** Many values have 1–5 passages; their top words are unstable.
   Mitigation: a minimum group size (default 3) for word-based metrics, and report how many groups
   were scored.
3. **Siblings share vocabulary by design.** Values of one dimension answer the same question, so
   sibling diversity is expected to be lower than diversity across dimensions. Never average the
   two; report them separately.
4. **Coverage differs between methods.** Topic models assign every passage (except an outlier
   topic); Delve leaves passages in "Other" and drops dimensions at selection. Always report
   **coverage** next to the metrics, otherwise a method can look better by discarding hard passages.
5. **Comparable preprocessing.** One reference corpus (the case corpus), one tokenizer, one stopword
   list and one N for all methods.
6. **Outcomes.** Outcome values (effects of decisions) are groups too, but they are not candidate
   decisions. The primary scores use candidate decisions only; scores including outcomes are a
   sensitivity row, with the outcome share per run (decision 2).

### 1.4 What the metrics will and will not support in the paper

- **Support:** "Delve's dimensions and values are as coherent/distinct as BERTopic topics (or more,
  or less) under the same procedure"; a familiar descriptive table for topic-modeling reviewers;
  a check that Delve's groups are not lexically incoherent.
- **Do not support:** claims about design-space quality or fidelity, or about the *meaning* of a
  dimension (a well-formed decision point can score low lexically). The paper states this
  explicitly (threat to validity).

---

## 2. Metric definitions

Notation: corpus `D` (all passages of the case), group `g` with document set `D_g`, top-N words
`W_g = (w_1 … w_N)` (default N = 10).

### 2.1 Top words per group (c-TF-IDF)

1. Tokenize every passage with one vectorizer (lowercase, `token_pattern` for words of ≥ 2
   letters, scikit-learn English stopwords plus an optional case stop list, `min_df = 2`,
   unigrams by default, optional bigrams).
2. For each group at a level, concatenate its documents into one class document; compute
   c-TF-IDF: `tf(w, g) · log(1 + A / f(w))`, with `A` the average number of words per class and
   `f(w)` the frequency of `w` across all classes at that level (BERTopic's definition).
3. `W_g` = the N highest-scoring words.

Classes are computed **per level** (all dimensions together; all values together), so IDF reflects
the competing groups at that level.

### 2.2 Coherence

- **NPMI (default, dependency-free):** document co-occurrence over the reference corpus `D`.
  For each pair `(w_i, w_j)` in `W_g`:
  `NPMI = log(P(w_i, w_j) / (P(w_i) P(w_j))) / −log P(w_i, w_j)`, with `P` estimated from document
  frequencies in `D`, and `NPMI = −1` when the pair never co-occurs (smoothing ε documented).
  Group coherence = mean over the `N(N−1)/2` pairs; level coherence = mean (and median) over groups.
- **C_V: deferred (decision 3).** Not implemented now; NPMI and the embedding variants cover lexical
  and conceptual coherence. Can be added later with gensim's `CoherenceModel(coherence="c_v")` on the
  same tokens and top words.

### 2.3 Diversity

- **TD (topic diversity):** `|∪_g W_g| / (K · N)` over the K groups of a level.
- **Sibling diversity (SD):** TD computed among the values of one dimension, averaged over
  dimensions with ≥ 2 scored values.
- **IRBO (optional):** inverted rank-biased overlap averaged over group pairs, rank-aware.

### 2.4 Cross-level (hierarchical)

- **Parent–child coherence (PCC):** for each dimension `d` and each of its values `v`, NPMI over the
  cross pairs `W_d × W_v` (excluding identical words); averaged. Higher = values are about their
  dimension.
- **Parent–child diversity (PCD):** `|W_d ∪ W_v| / (2N)` averaged over pairs. Higher = a value
  adds vocabulary beyond its dimension (it is not a restatement of the dimension).
- **Parent–non-child diversity (PnCD):** same as PCD for a dimension and the values of *other*
  dimensions. Should be higher than PCD.

### 2.5 Embedding-based variants (conceptual)

Using the run's embedding model (`text-embedding-3-small`, embeddings cached on disk per corpus):

- **Semantic coherence:** mean cosine similarity of a group's passages to its centroid (and mean
  pairwise cosine, for groups of ≥ 2).
- **Separation:** mean cosine distance between centroids of groups at a level; siblings separately.
- **Silhouette:** over the single-label assignment (dimension level; values within each dimension),
  which needs a partition (labels source, §3.2).

### 2.6 Reference points

- **Shuffled baseline:** recompute every metric after randomly permuting group memberships while
  keeping group sizes (k = 20 permutations, fixed seed); report mean ± sd. A method's score is
  meaningful only relative to its shuffled baseline.
- **Coverage:** share of corpus passages in at least one scored group, per level.

---

## 3. Inputs

### 3.1 A method-agnostic "groups" file

All methods are converted to one JSON format, and the scorer only reads that format:

```json
{
  "method": "delve" | "bertopic" | "tnt-llm" | "long-context",
  "run": "<source file>",
  "corpus": "examples/c2-rl-monitoring/c2-rl-monitoring_corpus.json",
  "groups_source": "evidence" | "labels",
  "levels": {
    "dimension": [{"id": "3", "label": "Drift Detection Test", "docs": ["s03_p02", "..."]}],
    "value": [{"id": "3.1", "label": "CUSUM", "parent": "3", "status": "accepted", "docs": ["..."]}]
  }
}
```

### 3.2 Delve adapter

From a run's taxonomy JSON (`selected_clusters` by default; `--iteration N` for another view) and,
for the labels source, the documents JSON:

- **`evidence` (default):** value docs = `supporting_doc_ids`; dimension docs = union of its values'
  docs. Covers every value, may overlap (a passage can support values of several dimensions).
- **`labels`:** dimension docs = passages labeled with that dimension; value docs = passages labeled
  with that value. A partition (needed for silhouette), but single-label labeling leaves many values
  with 0–1 passages.

**Decision 1: `evidence` is the source for all group metrics.** `labels` is used only for the
silhouette, which needs a partition, and is reported as such. The `--groups-source labels` option
stays available for sensitivity checks.

**Decision 2: candidate decisions only for the primary scores.** The adapter builds two group sets:
`candidates` (values with status `accepted`, `rejected` or `mixed`; dimension docs = union of those
values' docs), scored as the primary result, and `all` (outcomes included), scored as a sensitivity
row. The groups file records each value's `status`, so the same file serves both.

### 3.3 Baseline adapters (built with the baselines, paper plan §8.4)

- **BERTopic (L2):** topics → values; **BERTopic's own hierarchy** (`hierarchical_topics`, decision 4)
  → dimensions, cut at the level whose number of groups is closest to Delve's number of dimensions
  for the same case (the cut is recorded); outlier topic −1 excluded and counted against coverage.
- **TnT-LLM-style (L3):** Delve configuration, so the Delve adapter applies.
- **Long-context LLM (L1):** its JSON lists decisions, options and supporting passage ids, mapped to
  dimensions and values.

### 3.4 Corpus

The case corpus JSON (`<case>_corpus.json`, passages with ids). For runs without passage ids
(older examples), the documents JSON's `id`/`content` are used.

---

## 4. Outputs

- `<name>_topic_metrics_<timestamp>.json`: every metric per group and per level, with the
  shuffled baseline, coverage, settings (N, vectorizer, source, seed) and the scored/skipped group
  counts.
- A terminal panel and a markdown table:

| Level | Groups scored | Coverage | NPMI (shuffled) | TD | Embedding coherence (shuffled) | Separation |
|---|---|---|---|---|---|---|
| Dimension | 7/7 | 0.92 | 0.12 (0.03 ± 0.01) | 0.81 | 0.61 (0.48) | 0.37 |
| Value | 31/42 | 0.88 | … | … | … | … |
| Siblings | 6 dims | — | — | SD 0.74 | — | … |
| Cross-level | — | — | PCC … | PCD … / PnCD … | — | — |

(Numbers illustrative.) Rows are computed on candidate decisions; a second table repeats the value
and dimension rows with outcomes included, headed by the run's outcome share (e.g. "17 of 37 values are
outcomes").

---

## 5. Interface

```bash
python main.py --topic-metrics examples/c2-rl-monitoring/c2-rl-monitoring_taxonomy_<ts>.json \
               --corpus examples/c2-rl-monitoring/c2-rl-monitoring_corpus.json \
               --config examples/c2-rl-monitoring/c2_rl_monitoring_config.yaml \
               [--groups-source evidence|labels] [--top-n 10] [--min-docs 3] \
               [--no-embeddings] [--iteration N]
```

- A new standalone mode in `main.py`, mutually exclusive with `--visualize`, `--report`,
  `--evaluate`, like the existing ones.
- `--config` supplies the embedding model and the seed; `--no-embeddings` skips §2.5 (no API calls).
- A groups file (§3.1) can be passed instead of a taxonomy JSON, which is how baselines are scored.

---

## 6. Implementation units

| Unit | Content | Files | Effort |
|---|---|---|---|
| U1 | Groups format + Delve adapter (`evidence`, `labels`, `--iteration`; candidate and all-values group sets) | `src/taxonomy_generator/evaluation/topic_groups.py` | 0.5 d |
| U2 | Vectorizer, c-TF-IDF top words per level, NPMI, TD, SD, IRBO, PCC/PCD/PnCD | `src/taxonomy_generator/evaluation/topic_metrics.py` | 1 d |
| U3 | Embedding coherence, separation, silhouette; embedding cache per corpus | same module (+ reuse `utils.load_embeddings_model`, `l2_normalize`) | 0.5 d |
| U4 | Shuffled baseline and coverage | same module | 0.25 d |
| U5 | CLI mode, JSON artifact, terminal panel, markdown table | `main.py` | 0.5 d |
| U6 | ~~Optional C_V via gensim~~ — deferred (decision 3) | — | — |
| U7 | Baseline adapters (BERTopic, long-context) — with the baselines, not now | `baselines/` | with L1/L2 |

Total for U1–U5: about 2.75 days.

### Tests (no API calls)

- c-TF-IDF: a synthetic corpus where each group has distinctive words returns them as top words.
- NPMI: hand-computed values for a 4-document corpus; never-co-occurring pairs give −1.
- TD/SD: known values for overlapping and disjoint top-word lists.
- Cross-level: PCC higher for a value built from its parent's documents than for an unrelated one;
  PnCD > PCD in a synthetic two-dimension example.
- Shuffled baseline: coherent synthetic groups score above their shuffled baseline; seeded results
  repeat exactly.
- Adapter: evidence vs labels sources from a synthetic run (reuse `conftest.py` fixtures); groups
  below `--min-docs` are skipped and counted.
- Embedding metrics with a fake embedding model (fixed vectors).

---

## 7. Use in the paper

- **Where:** paper plan §5.1b (other fidelity measures) as a secondary, descriptive table per case
  (C1–C3), with the baselines once they exist; threats to validity cite caveat 1.3.1.
- **Comparisons:** Delve vs BERTopic vs TnT-LLM vs long-context, same groups format and settings;
  each with its shuffled baseline and coverage.
- **Nice-to-have, time permitting (decision 5):** apply the scorer to the **ground truth** itself (options with their source
  passages, if the gold alignment gives passage links) to show what coherence a human-made design
  space reaches — a useful reference for interpreting the numbers.

## 8. Decisions (2026-10-02)

1. **Value-level groups: evidence-linked passages** (`supporting_doc_ids`); dimension groups are the
   union of their values' passages. Labeled passages are used only for the silhouette.
2. **Outcomes: candidate decisions only for the primary scores.** Values with status `outcome` are
   excluded from the value groups, and dimension groups are the union of their candidate decisions'
   passages. Rationale: this measures the design space proper (decision points and their
   alternatives), matches the decision-point definition (outcomes are not candidate decisions) and the
   ground-truth options (outcomes correspond to forces/consequences), and does not swing with how many
   outcomes a run produced (0–46% of values in the runs of 2026-10-02). Every output also reports a
   **sensitivity row including outcomes** and the **outcome share** of values per run, which covers
   comparability with BERTopic (whose topics do not separate options from effects); at the dimension
   level the two differ by only a few passages.
3. **C_V: skipped for now** (no gensim); NPMI and the embedding variants are reported.
4. **BERTopic dimension level: BERTopic's own hierarchy** (`hierarchical_topics`), cut at the level
   closest to Delve's number of dimensions.
5. **Ground-truth scoring: nice-to-have, time permitting** (needs passage links per ground-truth
   option from the gold alignment).

## 9. Risks

- Low lexical coherence for good decision points may read as a weakness; the embedding variants,
  shuffled baselines and explicit framing (§1.4) address it.
- Small corpora (campus-bike: 28 documents) give unstable estimates; report them only for C1–C3.
- Metric definitions from the hierarchical topic-model literature must be checked against the
  original paper before reporting them under those names.
