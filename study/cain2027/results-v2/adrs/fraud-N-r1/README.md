# Architecture decisions: Card-fraud scoring service

* [Score transactions inline before authorization](0001-score-transactions-inline-before-authorization.md)
* [Scale the scoring service horizontally](0002-scale-the-scoring-service-horizontally.md)
* [Record model and feature provenance with each score](0003-record-model-and-feature-provenance-with-each-score.md)

## Decisions left open

* Model family, training process, and update cadence
* Feature definitions, sources, and freshness requirements
* Latency target within the stated tens of milliseconds
* Peak traffic volume, availability target, and overload behavior
* Audit record retention, access controls, and data protection
* Deployment environment and model rollout or rollback process
