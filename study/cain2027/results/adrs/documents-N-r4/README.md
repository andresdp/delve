# Architecture decisions: Large-scale document classification

* [how should classification work scale with volume](0001-how-should-classification-work-scale-with-volume.md)
* [how should results be shared with consuming teams](0002-how-should-results-be-shared-with-consuming-teams.md)
* [how should classification quality drift be detected](0003-how-should-classification-quality-drift-be-detected.md)

## Not grounded in the design space

* Document formats, ingestion sources, and preprocessing rules.
* Model provider, model selection, and update strategy.
* Classification taxonomy, confidence thresholds, and human review policy.
* Latency and availability targets.
* Data retention, privacy, security, and regulatory requirements.
* Result schema details and consumer delivery guarantees.
* Labeled-data source, sampling rate, and drift alert thresholds.
