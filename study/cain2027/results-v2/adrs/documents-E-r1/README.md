# Architecture decisions: Large-scale document classification

* [process documents in batches or in real time](0001-process-documents-in-batches-or-in-real-time.md)
* [how should prediction results be served](0002-how-should-prediction-results-be-served.md)
* [how should teams access stored results](0003-how-should-teams-access-stored-results.md)
* [how should production quality be monitored](0004-how-should-production-quality-be-monitored.md)
* [how should data be versioned](0005-how-should-data-be-versioned.md)
* [how should models be adjusted after monitoring finds drift](0006-how-should-models-be-adjusted-after-monitoring-finds-drift.md)

## Not grounded in the design space

* Per-document latency target and batch completion objective
* Quality metric, drift threshold, and alert routing
* Input and result retention, privacy, and access controls
* Model selection, training cadence, and validation criteria
* Seasonal capacity targets and recovery objectives
