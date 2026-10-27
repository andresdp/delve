# Architecture decisions: Card-fraud scoring service

* [Expose fraud scores through a REST prediction microservice](0001-expose-fraud-scores-through-a-rest-prediction-microservice.md)
* [Scale stateless scoring instances horizontally](0002-scale-stateless-scoring-instances-horizontally.md)
* [Scale scoring capacity elastically](0003-scale-scoring-capacity-elastically.md)
* [Deploy the model as a real-time service](0004-deploy-the-model-as-a-real-time-service.md)
* [Track model, feature, and dataset lineage across the lifecycle](0005-track-model-feature-and-dataset-lineage-across-the-lifecycle.md)
* [Serve online features from paired online and offline stores](0006-serve-online-features-from-paired-online-and-offline-stores.md)

## Decisions left open

* Score-level explanation format and method for auditors.
* Feature computation and point-in-time reconstruction semantics.
* Latency SLO percentile, timeout, and overload behavior.
* Peak capacity targets and failover scope.
* Audit retention, access controls, and tamper resistance.
