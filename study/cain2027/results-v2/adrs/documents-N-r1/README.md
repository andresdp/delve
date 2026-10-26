# Architecture decisions: Large-scale document classification

* [prioritize the system requirements](0001-prioritize-the-system-requirements.md)
* [how should classification work be dispatched](0002-how-should-classification-work-be-dispatched.md)
* [how should results be shared with teams](0003-how-should-results-be-shared-with-teams.md)
* [how should classification quality drift be surfaced](0004-how-should-classification-quality-drift-be-surfaced.md)

## Not grounded in the design space

* Classification latency target and whether results must be synchronous
* Inference cost or budget limits
* Reproducibility requirements and model or prompt versioning
* Document privacy, retention, and security requirements
* Label source, availability, and drift response process
* Required availability and recovery targets
