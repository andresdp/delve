# Architecture decisions: Large-scale document classification

* [Prioritize requirements](0001-prioritize-requirements.md)
* [Process documents through a durable asynchronous queue](0002-process-documents-through-a-durable-asynchronous-queue.md)
* [Expose results through a shared results interface](0003-expose-results-through-a-shared-results-interface.md)
* [Track classification quality by model and prompt version](0004-track-classification-quality-by-model-and-prompt-version.md)

## Decisions left open

* Classification latency or freshness targets
* Document privacy, security, and data residency constraints
* Classification taxonomy and confidence-based escalation rules
* Quality labels or review process for measuring drift
* Budget and model/provider constraints
* Retention, replay, and recovery requirements
* Consumer-specific access patterns and availability targets
