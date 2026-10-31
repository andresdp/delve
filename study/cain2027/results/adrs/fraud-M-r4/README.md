# Architecture decisions: Card-fraud scoring service

* [Serve fraud scores through a queue-fronted online cluster](0001-serve-fraud-scores-through-a-queue-fronted-online-cluster.md)
* [Expose predictions through a REST microservice](0002-expose-predictions-through-a-rest-microservice.md)
* [Deploy the scorer as a model-as-a-service](0003-deploy-the-scorer-as-a-model-as-a-service.md)
* [Track model, feature, and training lineage end to end](0004-track-model-feature-and-training-lineage-end-to-end.md)
* [Monitor service health and input quality in production](0005-monitor-service-health-and-input-quality-in-production.md)

## Decisions left open

* How transaction features are computed and served within the latency budget.
* How to explain individual fraud scores and preserve the exact feature values used for each decision.
* Fraud-label delay, retraining approval, and rollback policy.
* Authorization behavior when the scorer or feature dependencies are unavailable.
