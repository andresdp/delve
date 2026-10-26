# Architecture decisions: Card-fraud scoring service

* [score transactions inline before authorization](0001-score-transactions-inline-before-authorization.md)
* [scale the scoring service horizontally](0002-scale-the-scoring-service-horizontally.md)
* [record model and feature provenance with each score](0003-record-model-and-feature-provenance-with-each-score.md)

## Not grounded in the design space

* Model family, training process, and update cadence
* Feature definitions, sources, and freshness requirements
* Latency target within the stated tens of milliseconds
* Peak traffic volume, availability target, and overload behavior
* Audit record retention, access controls, and data protection
* Deployment environment and model rollout or rollback process
