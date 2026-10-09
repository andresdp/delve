# C3: Git at scale (no ground truth)

Third evaluation case (backlog items B6, B7, B9). Several organizations solved the same problem, making Git work at scale, in different ways. The case is evaluated without expert ground truth: expert rating, placement of each system as a point in the mined design space (A9, needs B7), and recall of stated trade-offs (needs B9).

## Corpora (B6)

**C3-raw (primary).** Five sources (`sources.csv`), fetched with `fetch_sources.py` and segmented by `build_corpus.py` exactly like C1/C2 (300-word target): 48 passages, 13.8k words.

| Id | Source | Passages |
|---|---|---|
| s1 | Cursor, "Git at any scale" (2026) | 16 |
| s2 | GitHub Engineering, "Stretching Spokes" | 6 |
| s3 | GitHub Engineering, "Building resilience in Spokes" | 9 |
| s4 | Microsoft, Scalar philosophy document (raw markdown override) | 2 |
| s5 | Azure DevOps Blog, "Introducing Scalar" | 15 |

Excluded: Wikipedia "Rendezvous hashing", listed in `examples/cursor-git-at-scale/references.md`. It describes a generic technique, not a system or decision.

**C3-curated (sensitivity).** The 16 paraphrased write-ups in `examples/cursor-git-at-scale/0[1-6]-*/`, unchanged. They are LLM-assisted paraphrases distilled from the article (their README says "generated 2026-08-20"), not author-written, and the paper describes them as such. `build_curated.py` writes the id-bearing copy `examples/c3-git-at-scale/c3-git-at-scale-curated_documents.json`. It reads only the six lens folders: the folder's own `build_corpus.py` would also pick up earlier Delve reports (`*_report_*.md`).

```bash
python benchmark/fetch_sources.py benchmark/c3-git-at-scale     # downloads (gitignored)
python benchmark/build_corpus.py c3-git-at-scale                 # C3-raw corpus (gitignored) + passage index
python benchmark/c3-git-at-scale/build_curated.py                # C3-curated with ids
python benchmark/check_c3_reference.py                           # B7/B9 against the passage index
```

The configs are in `examples/c3-git-at-scale/` (`c3_git_at_scale_config.yaml` for raw, `c3_git_at_scale_curated_config.yaml` for curated). They mirror C1, with four recorded C3 exceptions:
- output folder;
- `batch_size: 8`;
- `min_dimension_sources: 1` for raw (2 for curated);
- a use case that names the problem and the genre but no systems and no dimensions.

**Caveat on the sources.** C3-raw is uneven. Spokes (22 passages) and Scalar (17) have their own documentation. GitHub's filesystem distribution (3), Google's JGit/DHT (1) and Azure DevOps (1) appear only through the Cursor article's account. Their placement reflects that secondhand account, not the systems' own documentation.

## Status of B7 and B9

> **Agent draft (Claude, 2026-10-08). Author review pending.** Both files carry this status on their first line. The paper treats the unreviewed agent draft as primary (decision 2026-10-08) and the author-reviewed version as a sensitivity check.

**Bias guard.**
- **What the drafting agent read:** only the downloaded source texts, the C3-raw passages, the 16 curated write-ups and `references.md`.
- **What it never opened:** any Delve C3 output (`examples/cursor-git-at-scale/*_taxonomy_*`, `*_report_*`, `*_clusters_*`, `*_open_codes_*`, `*_documents_*`, `*_messages_*`, html reports, `graph.png`).
- **No C3 run yet:** both files were written before any C3 run with these configs.
- **Known exposure:** those earlier outputs come from an older pipeline version and use case, and the authors may have seen them.

**Rule for the review.** Change a row only against cited source text, and record each change (row, old value, new value, reason) in the review log below. Then the reviewed version stays auditable.

**Model families.** The drafting model (Claude) and the generation LLM (OpenAI `gpt-5.6-luna`) are different families. Both are LLMs, though, and may notice the same salient trade-offs.

## B7: passage → system map (`passage_systems.csv`)

Columns:
- `passage_id`: a C3-raw passage id `sNN_pKK`, or a curated document slug.
- `corpus`: `raw` or `curated`.
- `systems`: every system the passage substantively describes, `;`-separated.
- `primary`: the system the passage is mainly about; `GENERAL` for even comparisons.
- `basis`: a one-line note in the agent's own words.

| Code | System |
|---|---|
| `GH-FS` | GitHub before Spokes: NFS, GFS, DRBD filesystem distribution, then single-copy RPC fileservers |
| `GOOG-DHT` | Google: JGit with objects in a distributed hash table |
| `GH-SPOKES` | GitHub Spokes (formerly DGit): plain repositories replicated with three-phase commit |
| `MS-GVFS` | Microsoft VFS for Git (GVFS): virtualized filesystem and the GVFS protocol with cache servers |
| `MS-SCALAR` | Microsoft Scalar: upstream partial clone, sparse-checkout, background maintenance |
| `MS-ADO` | Azure DevOps: packfiles in blob storage, references in a relational database |
| `CUR-CONT` | Cursor Continuity and its production platform Origin: write-ahead log in S3 |
| `GENERAL` | Git internals or problem framing, no specific system |

**Successor rule.** A successor gets its own code when its source says it reversed a design decision: Scalar dropped GVFS's virtualization, and Spokes replaced filesystem distribution. It shares a code when it deploys the same design, as Origin does Continuity.

**Placement (A9).** Placement aggregates by `systems` membership. `primary` only breaks ties between conflicting values.

| System | Raw passages (member / primary) | Curated documents (member / primary) |
|---|---|---|
| GH-SPOKES | 22 / 19 | 11 / 4 |
| MS-SCALAR | 17 / 16 | 3 / 1 |
| CUR-CONT | 7 / 7 | 11 / 2 |
| MS-GVFS | 6 / 1 | 3 / 0 |
| GH-FS | 3 / 2 | 4 / 1 |
| GOOG-DHT | 1 / 1 | 3 / 1 |
| MS-ADO | 1 / 0 | 1 / 1 |
| GENERAL | 3 / 2 | 6 / 6 |

`MS-ADO` has no raw passage as primary. It is described only in the second half of `s01_p15`, which is mainly about Continuity, so it is placeable only through membership.

## B9: silver trade-off list (`silver_tradeoffs.csv`)

Columns:
- `id`, `tradeoff`: one sentence in the agent's own words.
- `systems`.
- `qa_favoured`, `qa_sacrificed`: ISO 25010 characteristics (sub-characteristic in parentheses), plus cost and scalability.
- `explicitness`: `stated`, when the source names both sides, or `implied`.
- `passage_ids`: C3-raw evidence, required.
- `curated_ids`: curated write-ups covering the same trade-off.
- `found_in`: `raw`, or `curated-check` when a miss was found in the curated write-ups.

Drafted from the C3-raw passages only. The curated documents were then checked for misses and added none. All 20 trade-offs are `stated` and `found_in=raw`; 7 have no curated counterpart. Recall against this list is **indicative only**: it is a silver reference written by an LLM agent, not an expert ground truth.

## Review checklist (authors)

- [ ] B7: each row's systems and primary match the passage. Check especially the mixed passages `s01_p03`, `s01_p10`, `s01_p11`, `s01_p13`, `s01_p15`, `s02_p02`, `s05_p08`.
- [ ] B7: the vocabulary and the successor rule (GVFS vs Scalar, filesystem distribution vs Spokes).
- [ ] B9: each trade-off is stated in the cited passages, and the quality attributes are right.
- [ ] B9: no stated trade-off is missing.
- [ ] Use case of both C3 configs agreed by two authors.

## Review log

| Date | Reviewer | File / row | Old | New | Reason (cited text) |
|---|---|---|---|---|---|
