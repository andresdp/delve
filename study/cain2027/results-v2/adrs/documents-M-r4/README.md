# Architecture decisions: Large-scale document classification

* [how should document classifications be computed and delivere](0001-how-should-document-classifications-be-computed-and-delivere.md)
* [how should production quality drift be detected](0002-how-should-production-quality-drift-be-detected.md)
* [how should compute capacity respond to seasonal workload](0003-how-should-compute-capacity-respond-to-seasonal-workload.md)
* [how should inference be packaged and deployed](0004-how-should-inference-be-packaged-and-deployed.md)

## Not grounded in the design space

* LLM provider, classifier model, and prompt/version strategy.
* Ground-truth collection and label delay for measuring classification quality.
* Document privacy, retention, and insurer-specific regulatory controls.
* Batch cadence, freshness target, and any per-document latency service level.
