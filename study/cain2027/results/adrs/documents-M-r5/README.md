# Architecture decisions: Large-scale document classification

* [how should compute scale with demand](0001-how-should-compute-scale-with-demand.md)
* [how should incoming documents enter processing](0002-how-should-incoming-documents-enter-processing.md)
* [when should predictions be computed](0003-when-should-predictions-be-computed.md)
* [how should runtime components communicate](0004-how-should-runtime-components-communicate.md)
* [how should results be exposed to consuming teams](0005-how-should-results-be-exposed-to-consuming-teams.md)
* [how should production quality be monitored](0006-how-should-production-quality-be-monitored.md)
* [how should ml workflow steps be coordinated](0007-how-should-ml-workflow-steps-be-coordinated.md)

## Not grounded in the design space

* LLM provider, model choice, and inference cost controls.
* Claim taxonomy, confidence thresholds, and fallback handling.
* Label collection and ground-truth timing for quality measurement.
* Retention, privacy, and access controls for insurance documents.
* Consumer-specific freshness, availability, and delivery guarantees.
