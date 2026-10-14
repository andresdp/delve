# C3 reference candidate (2026-10-10)

A full C3 (Git at scale) run with no cap on the number of dimensions, made with the relation rules of
`feat/dimension-relations`: relation types read as sentences and are checked for direction, splits keep a
dimension's relations on one part, and each dimension keeps at most 3 relations. It is a candidate to replace
the current C3 study run (`../c3-git-at-scale_taxonomy_20261008_115350.json`), which predates these rules.

- **Settings:** [`../c3_git_at_scale_config.yaml`](../c3_git_at_scale_config.yaml), unchanged; `openai/gpt-5.6-luna`
  for every LLM role.
- **Result (selected view):** 31 dimensions, 191 values, 11 relations (7 affects, 3 constrains, 1 requires), at most
  1 relation per dimension, none related both ways.
- **Design points:** 180 sampled points (attested, novel and control; 2 or 3 dimensions; 30 per group and size,
  seed 42), each with a short LLM description.
- **Not committed:** the outputs that quote the corpus (documents, clusters, open codes, messages, HTML report) and
  the wiki, as for the study run. Rebuild the wiki with:

```bash
RUN=examples/c3-git-at-scale/reference-candidate-20261010/c3-git-at-scale_taxonomy_20261010_215639
python benchmark/export_wiki.py $RUN.json \
       --corpus examples/c3-git-at-scale/c3-git-at-scale_corpus.json \
       --sources benchmark/c3-git-at-scale/sources.csv \
       --systems benchmark/c3-git-at-scale/passage_systems.csv \
       --system-names benchmark/c3-git-at-scale/systems.csv \
       --design-points ${RUN}_design_points.json \
       --config examples/c3-git-at-scale/c3_git_at_scale_config.yaml --evaluation
```

One run only: run-to-run variation in the number of dimensions is large (19 to 31 in the runs of 2026-10-10), so
compare more than one run before adopting it as the reference.
