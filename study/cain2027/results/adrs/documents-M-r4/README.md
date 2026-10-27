# Architecture decisions: Large-scale document classification

* [Use scheduled batch prediction for document classification](0001-use-scheduled-batch-prediction-for-document-classification.md)
* [Scale classification resources elastically](0002-scale-classification-resources-elastically.md)
* [Expose classifications through a REST prediction microservice](0003-expose-classifications-through-a-rest-prediction-microservic.md)
* [Monitor service health and data quality in production](0004-monitor-service-health-and-data-quality-in-production.md)

## Decisions left open

* How incoming documents are ingested and validated.
* How classifications are persisted and made available to consumer teams.
* How classifier versions are evaluated, approved, and rolled back.
* How drift alerts lead to investigation or model updates.
* Document privacy, retention, and access controls.
