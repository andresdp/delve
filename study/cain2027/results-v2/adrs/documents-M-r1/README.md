# Architecture decisions: Large-scale document classification

* [how should incoming documents be scored](0001-how-should-incoming-documents-be-scored.md)
* [how should runtime capacity respond to seasonal demand](0002-how-should-runtime-capacity-respond-to-seasonal-demand.md)
* [how should classification quality drift be detected](0003-how-should-classification-quality-drift-be-detected.md)

## Not grounded in the design space

* The LLM model, provider, and inference-cost strategy.
* Document ingestion, retries, deduplication, and ordering guarantees.
* The result contract, persistence, and access controls for consuming teams.
* Label collection and evaluation policy for delayed quality measurement.
* Data privacy, retention, and security requirements.
