# Architecture decisions: Large-scale document classification

* [how should predictions be served](0001-how-should-predictions-be-served.md)
* [how should runtime capacity handle seasonal volume](0002-how-should-runtime-capacity-handle-seasonal-volume.md)
* [how should classification quality be monitored](0003-how-should-classification-quality-be-monitored.md)
* [how should input drift be detected](0004-how-should-input-drift-be-detected.md)

## Not grounded in the design space

* LLM model selection, hosting, token limits, and inference cost.
* Document ingestion format, source integration, and queueing or retry policy.
* Result schema, access controls, and delivery contract for consuming teams.
* Batch cadence, freshness target, and service-level objectives.
