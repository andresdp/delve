# Architecture decisions: Card-fraud scoring service

* [Model as a service](0001-model-as-a-service.md)
* [Microservice based model serving](0002-microservice-based-model-serving.md)
* [Feature store](0003-feature-store.md)
* [N versions in production](0004-n-versions-in-production.md)
* [Data version repository](0005-data-version-repository.md)
* [Model in-production tracking](0006-model-in-production-tracking.md)
* [Prediction service performance testing](0007-prediction-service-performance-testing.md)

## Decisions left open

* How to provide a highly available deployment across zones or regions.
* How to define the latency percentile and timeout/fallback behavior for authorization.
* How to protect cardholder data and control access to retained feature and score records.
* How to retain audit evidence and model artifacts for the required period.
