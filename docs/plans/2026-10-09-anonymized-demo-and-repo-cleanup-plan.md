---
title: Anonymized demo branch for review, and cleanup of the public repository
date: 2026-10-09
status: plan (nothing done yet; the author re-assesses closer to the deadline)
related: docs/paper/SANER2027_Delve_Draft.md §9.5 (anonymity), docs/paper/PRE_FREEZE_TODO.md
---

# Anonymized demo branch and repository cleanup

**Goal.** The repository stays public under its current name. For the double-anonymous SANER review, the paper
links an anonymized mirror of a separate, compact `demo` branch, served by **Anonymous GitHub**
(anonymous.4open.science, the "Anonymous4Science" service). Before that, `main` is tidied and stale branches are
deleted.

**Constraint.** The repository sits in iCloud-synced `~/Documents`. There are two rules:
- **Never rewrite history:** no force-push, no filter-repo.
- **Branch deletions need the author's explicit go-ahead,** given one branch list at a time.

## Part A — clean up `main` and the branches

### A1. Stale branches (checked 2026-10-09)

Every `feat/*` branch on `origin` is merged into `main`:
- `feat/c3-git-at-scale`, `feat/design-space-wiki`, `feat/ground-truth-matcher`, `feat/grounded-theory-report`;
- `feat/reusable-taxonomies`, `feat/saner27-paper`, `feat/taxonomy-evaluation-feedback-integration`;
- `feat/taxonomy-evaluation-suite`, `feat/tool-based-taxonomy-update`, `feat/unified-html-report`.

The same branches exist locally.

- [ ] Delete the merged branches on `origin` (`git push origin --delete <branch>`) and locally (`git branch -d`, which refuses unmerged branches).
- [ ] `feat/saner27-paper`: merged, but it was the paper branch. Confirm nothing on it is needed before deleting it; paper work now lives on `feat/paper-and-experiments`.
- [ ] `upstream/hitl` and `upstream/main` exist on `origin` as branches. They are pushed copies of the original Delve repository, not merged. Decide whether to keep them, for the fork's lineage, or delete them.
- [ ] After merging, the GitHub setting "automatically delete head branches" keeps this tidy.

### A2. Contents of `main`

Candidates to remove from `main` going forward. Deleting a file does not remove it from history; that is acceptable for the public repo, which stays under the authors' names anyway.

- [ ] **Third-party PDFs in `papers/`:** Shaw; TnT-LLM; the C1 and C2 case-study papers; the MARL study. These are copyrighted papers in a public repository.
  - Replace them with a `papers/README.md` that lists the references and links.
  - Keep `papers/delve_design_space.pptx` only if it is meant to be public; check it for author names.
- [ ] **Internal planning material:**
  - `docs/plans/`, `docs/paper/` (plan, to-do list, draft notes), `docs/solutions/`, `openwiki/`;
  - the design notes `docs/*.md`, which are many and partly superseded.

  Options:
  - keep them, since they are useful history;
  - move them to an `archive/` folder;
  - keep only the current ones.

  Decide per folder. The paper draft must not be on `main` before acceptance if it contains author notes.
- [ ] **Example runs:** old runs in `examples/*` from development, e.g. several C1/C2 runs and campus-bike runs. Keep the runs the README and USAGE refer to, plus those the paper will cite after the freeze.
- [ ] **Duplicate or iCloud leftovers:** search tracked files for names ending in ` 2` or ` 3`.
- [ ] **README and USAGE:** check that every link still resolves after the removals.

## Part B — the anonymized `demo` branch

### B1. Shape

- **An orphan branch `demo`:** no shared history with `main`, a single commit per update, committed as `Anonymous <anonymous@example.org>`. The anonymized mirror shows files, not history, but an orphan branch also keeps the branch small and free of old commit messages.
- **Generated, not edited:** a script copies an allow-list of paths from a pinned `main` commit, applies the anonymization edits (B3), and commits to `demo`. It is re-run for each update: the submission, then camera-ready corrections if needed. Suggested location: `scripts/make_demo_branch.sh` on `main`, itself free of names.
- **Pinned for review:** Anonymous GitHub can follow a branch or a commit; use the commit created for the submission.

### B2. Contents (allow-list proposal)

| Include | Why |
|---|---|
| `src/taxonomy_generator/` (code, prompts, wiki templates, assets), `main.py`, `pyproject.toml`, `config.yaml`, `requirements*` | The approach |
| `tests/` | Shows the implementation is tested |
| `benchmark/` scripts and READMEs, `benchmark/*/sources.csv`, `benchmark/*/gt/` | The evaluation kit. Source texts are never included: they are gitignored and re-fetched by script. |
| Study configs `examples/c1-ml-workflow/*config*.yaml`, `examples/c2-rl-monitoring/…`, `examples/c3-git-at-scale/…` | Exact settings |
| The frozen study runs (taxonomy JSON, reports, match results) once they exist | The results in the paper |
| `examples/c3-git-at-scale/sample/` with its wiki | The browsable example |
| An anonymized `README.md`, `USAGE.md`, `CONCEPTS.md`, `LICENSE` | Entry points |

Excluded:
- `docs/plans`, `docs/paper`, `docs/solutions`, `openwiki/`, `papers/`;
- development runs;
- `.github/`, `CLAUDE.md`, `AGENTS.md`, `graphify-out/`;
- anything gitignored.

### B3. Anonymization edits

1. **Term scan (not yet run).** Search every included file for:
   - author names and handles: `andresdp`, `adiazpace`, the co-authors' names;
   - institutions and their abbreviations, e.g. ISISTAN, UNICEN, and the co-authors' institutions;
   - email addresses and absolute paths (`/Users/…`);
   - the repository URL (`github.com/andresdp/delve`) and the Pages URL (`andresdp.github.io`);
   - the upstream fork's URL;
   - acknowledgements, grant numbers.

   The script fails if any term remains after the edits.
2. **Known spots to edit:**
   - `LICENSE` copyright line;
   - `pyproject.toml` authors and URLs;
   - README badges, links and acknowledgements;
   - the README "Browse a sample wiki online" link, which points to Pages: remove it, or point it to the anonymized mirror;
   - the sample wiki's `raw/run.json`, which records input paths: check for absolute paths, and re-export or rewrite them as relative paths.
3. **Anonymous GitHub's own term replacement:** the service replaces a configured term list (e.g. `andresdp` → `XXXX`) in text files when serving. Use it as a second safety net, not the only one: it does not edit binary files (images, PDFs, `.pptx`) and can leave odd text behind.
4. **Binary files:** check the SVG logos and icons, which are text and may carry metadata. Keep no PDFs or Office files on `demo`.

### B4. Anonymous GitHub setup (author's account)

- [ ] On anonymous.4open.science, log in with GitHub and anonymize `andresdp/delve`, branch `demo`, pinned to the submission commit.
- [ ] Add the term list from B3 and set an expiry date after the review period.
- [ ] Check the current size and file-count limits; the sample wiki adds about 9.6 MB in 225 pages. Exclude the 7.4 MB HTML report if needed.
- [ ] Check whether the service's website view serves the wiki's HTML (pages, d3, CSS). If it does not, the README on `demo` explains how to download it and open `html/index.html`.
- [ ] Put the mirror's URL in the paper's artifact sentence (draft §4.7 TODO) and open it in a private browser window to check it as a reviewer would.

### B5. Residual risk

- **Searchable public repo:** the repository stays public and the tool name (Delve, DelveDSpace) appears in the paper, so a reviewer who searches could find it. This is usually acceptable under double-anonymous rules, which forbid revealing identity, not having public work. Check SANER 2027's policy on public repositories and preprints. If it requires more, the option is to keep the public repo but avoid the tool's distinctive name in the paper, e.g. by calling it "our approach".
- **Fork link:** the fork relation to the original Delve repository is visible on GitHub, but not in the anonymized mirror.

## Development history and unused features (author's request, 2026-10-09)

**Principle.** `demo` must not reveal how the project evolved. Only the approach as evaluated, its evaluation kit and its results go there.

**Exclude from `demo`, beyond B2:**
- **Interim results:** `docs/paper/results/`, e.g. the 2026-10-05 update-strategy comparison and the 2026-10-08 quality probe.
- **Development runs:** every run that is not a frozen study run. This includes, for example, `examples/c1-ml-workflow/u7/`, earlier C1/C2 runs and the campus-bike runs.
- **History-revealing documents:** `benchmark/README.md` sections such as "Changes after scores were seen", progress logs and status notes in other READMEs, and plan, design and roadmap documents. Where a README is needed (benchmark, cases), write a short version for `demo` that describes the current kit only.
- **History in code:** comments that record decisions with dates or "before/after" notes, e.g. config comments like "decided 2026-10-08" and "C3:" exceptions. Keep the settings themselves; reword the comments neutrally where the demo script can do it safely, or accept them if they reveal nothing about the authors.
- **Planning docs on `main`:** decide in A2 whether they stay public on `main`. If they do, they stay off `demo` either way.

**Deprecating features the evaluated pipeline does not use.** Candidates, each to be checked against the frozen study configs before any decision:

| Feature | Used by the study? | Note |
|---|---|---|
| `edit_mode: rewrite` | Yes, ablation (c) | Keep |
| `edit_mode: rewrite_restore` | No: a development control | Candidate to remove or hide |
| `relevance_selection` (LLM relevance filter) | Off in the study | Candidate: keep the switch, default off; or remove |
| Summarization before coding | Skipped in the study (`skip: true`) | Candidate: keep as an option, or remove |
| Per-iteration biplots (`visualization`) | Final view only, if at all | Check |
| Multi-run consistency comparison (`--evaluate run1 run2 …`) | Possibly, for stability (RQ3) | Check before removing |
| Test mode, seeded taxonomies, feedback files (reusable taxonomies) | Not in the RQs | Candidate to keep as documented options |
| Older reports (Markdown report, HTML report) | Useful as outputs | Keep |
| `selection_variant.py` and similar development scripts in `benchmark/` | Development only | Candidate to exclude from `demo` |

**Timing.** Removing code paths changes the pipeline, so do not do it before or during the frozen runs. Two options:
1. Deprecate on `main` after the main runs, re-running the unit tests and checking that the study configs still load and give the same results.
2. Leave `main` as is and exclude the unused paths only on `demo`. This is riskier: the demo code would differ from the code that produced the results.

Option 1 is safer for reproducibility; decide closer to the deadline.

## Term scan results (2026-10-09, `main` at `e86c319`)

**Scope.** Tracked text files on `main`; binary files (PDFs, `.pptx`, images) were skipped. The terms were:
- `andresdp`, `adiazpace`, `diazpace`, `diaz pace` / `díaz pace`, `andres diaz`;
- `isistan`, `unicen`, `conicet`, `tandil`;
- `/Users/`, `andresdp.github.io`, `github.com/andresdp`.

**Not yet scanned:** the co-authors' names and institutions, which the author needs to supply.

| Where | What | Action for `demo` |
|---|---|---|
| `README.md:23`, `USAGE.md:167`, `examples/c3-git-at-scale/sample/README.md:16` | Link to `https://andresdp.github.io/delve/` | Remove, or point to the anonymized mirror |
| `README.md:121` | `git clone https://github.com/andresdp/delve.git` | Replace with a placeholder (`git clone <repository-url>`) |
| `.github/workflows/sample-wiki-pages.yml:4` | Pages URL in a comment | Excluded anyway (`.github` is not on `demo`) |
| `docs/plans/2026-10-07-…-c3-git-at-scale-…-plan.md:305` | `/Users/adiazpace/…` path | Excluded anyway (`docs/plans` is not on `demo`) |
| C3 sample `*_clusters_*.json`, `*_documents_*.json` | `/Users/stolee/…`: paths quoted from Microsoft's Scalar documentation (source text, a third party) | No action |
| Sample wiki `raw/run.json` | No `/Users/` paths found | No action |
| Commit history | 208 commits by `andresdp <adiazpace@gmail.com>` | The orphan `demo` branch has no history |

**Not identifying the paper's authors, but worth deciding:**
- **Original Delve author:** `LICENSE` (`Copyright (c) 2024 Andres Torres`) and `pyproject.toml` (`authors`) name the original author. The MIT license requires keeping the copyright notice, so keep it on `demo`. Adding a line for the new authors is a camera-ready step, not a review step.
- **The fork link:** README "Background and acknowledgements" links `andrestorres123/delve`, whose fork list leads to `andresdp/delve`. It is a weak link, because a reviewer would have to follow the fork network. Options: keep the credit (fair and license-friendly), or on `demo` name the project without linking it.
- **Git remote `upstream`:** points to `andrestorres123/delve`. This is local configuration, not in any file, so no action.

**Conclusion.** Few files identify the authors, and all of them are links or are in folders excluded from `demo`. The demo script needs only:
- three link edits;
- one clone-URL edit;
- a decision on the fork link;
- a final scan that includes the co-authors' names.

## Order

1. Run the term scan (B3.1) to size the work.
2. Part A: branch deletions (A1, after the author confirms each list), then `main` contents (A2, decided per folder).
3. Write the demo script and create `demo` after the freeze, once the study runs exist, so the branch is built once with the final results.
4. Set up Anonymous GitHub before 10-23, then put the link in the paper.
