# Architecture decisions: Large-scale document classification

* [how should documents reach the classifier](0001-how-should-documents-reach-the-classifier.md)
* [how should llm classification be served](0002-how-should-llm-classification-be-served.md)
* [how should classification results reach consuming teams](0003-how-should-classification-results-reach-consuming-teams.md)
* [how should classification quality drift be detected](0004-how-should-classification-quality-drift-be-detected.md)

## Not grounded in the design space

* Classification taxonomy, confidence thresholds, and handling of ambiguous or unsupported documents.
* Latency and freshness targets for classification and consumer delivery.
* Data sensitivity, retention, residency, and approved LLM provider constraints.
* Label source, volume, and delay for quality measurement.
* Model evaluation, release, rollback, and retraining ownership.
* Availability, recovery, and delivery guarantees expected of the system.
