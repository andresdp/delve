# Architecture decisions: Large-scale document classification

* [how should source documents enter the workflow](0001-how-should-source-documents-enter-the-workflow.md)
* [when should predictions be computed](0002-when-should-predictions-be-computed.md)
* [how should runtime capacity respond to seasonal demand](0003-how-should-runtime-capacity-respond-to-seasonal-demand.md)
* [how should production quality and drift be monitored](0004-how-should-production-quality-and-drift-be-monitored.md)
* [how should ml workflow stages be coordinated](0005-how-should-ml-workflow-stages-be-coordinated.md)
* [how should teams access classification results](0006-how-should-teams-access-classification-results.md)

## Not grounded in the design space

* Document arrival-to-classification freshness target and batch cadence.
* Required throughput and seasonal peak sizing targets.
* Label availability and the quality metric or drift threshold that should alert operators.
* Retry, deduplication, ordering, and failure recovery for document ingestion.
* Result retention, access controls, and audit requirements for insurer data.
* Model family, prompt design, and evaluation policy for the LLM classifier.
