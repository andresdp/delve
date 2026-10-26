# Architecture decisions: Card-fraud scoring service

* [Queue-fronted online serving cluster](0001-queue-fronted-online-serving-cluster.md)
* [REST prediction microservice](0002-rest-prediction-microservice.md)
* [Online/offline feature-store architecture](0003-online-offline-feature-store-architecture.md)
* [Data-to-model lineage management](0004-data-to-model-lineage-management.md)
* [Service-health and data-quality monitoring](0005-service-health-and-data-quality-monitoring.md)

## Decisions left open

* Fraud-score explanation format and per-transaction audit record schema.
* Availability target, fail-open or fail-closed behavior, and authorization timeout policy.
* Feature retention period, access controls, and audit retention requirements.
* Model choice, fraud-specific evaluation criteria, and promotion thresholds.
