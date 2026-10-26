# Architecture decisions: Large-scale document classification

* [Scheduled batch prediction deployment](0001-scheduled-batch-prediction-deployment.md)
* [Elastic resource scaling](0002-elastic-resource-scaling.md)
* [REST prediction microservice](0003-rest-prediction-microservice.md)
* [Combined input-drift and prediction-quality monitoring](0004-combined-input-drift-and-prediction-quality-monitoring.md)

## Decisions left open

* How labels are produced and how often they become available.
* Whether and when detected drift should trigger retraining or human review.
* Required latency, freshness, availability, and seasonal peak capacity targets.
* Classification result retention, access control, and privacy requirements.
* The schema, delivery mechanism, and ownership expectations for each consuming team.
