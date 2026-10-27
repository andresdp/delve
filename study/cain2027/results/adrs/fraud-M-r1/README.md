# Architecture decisions: Card-fraud scoring service

* [Use queue-fronted online serving for transaction scores](0001-use-queue-fronted-online-serving-for-transaction-scores.md)
* [Expose predictions through a REST microservice](0002-expose-predictions-through-a-rest-microservice.md)
* [Serve prepared features from an online feature pipeline](0003-serve-prepared-features-from-an-online-feature-pipeline.md)
* [Track model, feature, and training lineage for each release](0004-track-model-feature-and-training-lineage-for-each-release.md)
* [Monitor service health and data quality in production](0005-monitor-service-health-and-data-quality-in-production.md)

## Decisions left open

* Fraud model family, training and evaluation method, and score-to-authorization policy.
* The specific explanation method and audit record schema, including feature values per score.
* Feature freshness and fallback behavior when online features are unavailable.
* Availability targets, recovery objectives, capacity limits, and deployment topology.
