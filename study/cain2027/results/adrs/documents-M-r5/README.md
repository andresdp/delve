# Architecture decisions: Large-scale document classification

* [Use scheduled batch scoring for document classification](0001-use-scheduled-batch-scoring-for-document-classification.md)
* [Scale runtime resources elastically with workload demand](0002-scale-runtime-resources-elastically-with-workload-demand.md)
* [Monitor input and feature drift in production](0003-monitor-input-and-feature-drift-in-production.md)

## Decisions left open

* How document data is ingested, retained, and governed, including insurer privacy and access controls.
* How classifier labels and model quality are evaluated, and how false positives and false negatives are weighted.
* How scoring schedules, freshness targets, and workload partitioning are set.
* How classification outputs are versioned and delivered consistently to consuming teams.
* How model changes are approved, deployed, and rolled back.
