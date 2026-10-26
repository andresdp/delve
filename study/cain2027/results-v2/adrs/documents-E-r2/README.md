# Architecture decisions: Large-scale document classification

* [how should documents enter the system](0001-how-should-documents-enter-the-system.md)
* [should classification processing be batched or real time](0002-should-classification-processing-be-batched-or-real-time.md)
* [how should predictions be served](0003-how-should-predictions-be-served.md)
* [how should classification data and results be shared](0004-how-should-classification-data-and-results-be-shared.md)
* [how should production classification be monitored](0005-how-should-production-classification-be-monitored.md)
* [how should the model be adjusted when monitoring finds drift](0006-how-should-the-model-be-adjusted-when-monitoring-finds-drift.md)

## Not grounded in the design space

* Target classification latency and acceptable result staleness
* How to measure quality drift and obtain labels or ground truth
* LLM provider, model selection, prompt/version management, and reproducibility
* Retry, deduplication, and failure handling for large batch runs
* Data privacy, retention, and access controls across teams
* Capacity, cost, and scaling strategy for seasonal peaks
