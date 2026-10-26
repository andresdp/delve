# Architecture decisions: Card-fraud scoring service

* [REST prediction microservice](0001-rest-prediction-microservice.md)
* [Model-as-a-service deployment](0002-model-as-a-service-deployment.md)
* [Online computation serving](0003-online-computation-serving.md)
* [Online/offline feature-store architecture](0004-online-offline-feature-store-architecture.md)
* [Comprehensive ML lifecycle traceability](0005-comprehensive-ml-lifecycle-traceability.md)
* [Elastic resource scaling](0006-elastic-resource-scaling.md)

## Decisions left open

* Fraud-model family and decision threshold selection
* Authorization behavior when scoring or feature retrieval fails
* Audit retention period and access policy for transaction-level records
* Regional failover and recovery objectives
* Training labels, retraining cadence, and model promotion policy
