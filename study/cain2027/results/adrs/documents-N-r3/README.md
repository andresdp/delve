# Architecture decisions: Large-scale document classification

* [how should documents enter classification](0001-how-should-documents-enter-classification.md)
* [how should inference scale with seasonal demand](0002-how-should-inference-scale-with-seasonal-demand.md)
* [how should classification results reach consuming teams](0003-how-should-classification-results-reach-consuming-teams.md)
* [how should classification quality drift be surfaced](0004-how-should-classification-quality-drift-be-surfaced.md)
* [how should classifier updates be introduced](0005-how-should-classifier-updates-be-introduced.md)

## Not grounded in the design space

* Document formats, sizes, and ingestion interfaces
* Claim type taxonomy and labeled quality data
* LLM provider, model, and deployment constraints
* Latency and backlog service objectives
* Data retention, privacy, and security requirements
* Quality metrics, alert thresholds, and operator response process
* Event delivery guarantees and consumer replay needs
