# Architecture decisions: Large-scale document classification

* [Use an asynchronous queue to scale document classification](0001-use-an-asynchronous-queue-to-scale-document-classification.md)
* [Publish classifications through a shared results interface](0002-publish-classifications-through-a-shared-results-interface.md)
* [Track classification quality over time](0003-track-classification-quality-over-time.md)
* [Version models and classification outputs](0004-version-models-and-classification-outputs.md)

## Decisions left open

* Claim-type taxonomy and whether classes are hierarchical.
* Document formats, languages, and preprocessing requirements.
* Latency and availability targets for classification and result access.
* Whether the LLM is hosted or self-managed, and its selection criteria.
* Data residency, privacy, retention, and security requirements.
* Source and labeling process for quality outcomes.
* Human review, escalation, and correction workflow.
* Retry, deduplication, and failure-handling requirements.
* Consumer access patterns and result retention needs.
