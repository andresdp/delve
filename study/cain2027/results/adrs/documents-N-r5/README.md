# Architecture decisions: Large-scale document classification

* [how should documents enter classification](0001-how-should-documents-enter-classification.md)
* [how should classification capacity scale](0002-how-should-classification-capacity-scale.md)
* [how should the llm classifier be invoked](0003-how-should-the-llm-classifier-be-invoked.md)
* [how should classification results reach consumers](0004-how-should-classification-results-reach-consumers.md)
* [how should classification output be constrained](0005-how-should-classification-output-be-constrained.md)
* [how should classification quality drift be detected](0006-how-should-classification-quality-drift-be-detected.md)

## Not grounded in the design space

* Document format and preprocessing requirements
* Claim-type taxonomy ownership and change process
* Latency, availability, and recovery targets
* PII handling, data residency, and retention constraints
* Human review and escalation policy for uncertain classifications
* Provider selection, quotas, and cost limits
