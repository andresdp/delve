# Architecture decisions: Large-scale document classification

* [ETL-based feature ingestion](0001-etl-based-feature-ingestion.md)
* [Scheduled batch prediction deployment](0002-scheduled-batch-prediction-deployment.md)
* [Elastic resource scaling](0003-elastic-resource-scaling.md)
* [Input and feature-drift monitoring](0004-input-and-feature-drift-monitoring.md)
* [Orchestrated ML pipeline](0005-orchestrated-ml-pipeline.md)
* [REST prediction microservice](0006-rest-prediction-microservice.md)

## Decisions left open

* Document arrival-to-classification freshness target and batch cadence.
* Required throughput and seasonal peak sizing targets.
* Label availability and the quality metric or drift threshold that should alert operators.
* Retry, deduplication, ordering, and failure recovery for document ingestion.
* Result retention, access controls, and audit requirements for insurer data.
* Model family, prompt design, and evaluation policy for the LLM classifier.
