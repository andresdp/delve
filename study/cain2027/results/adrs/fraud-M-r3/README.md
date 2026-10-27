# Architecture decisions: Card-fraud scoring service

* [Track the full ML lifecycle for auditable scores](0001-track-the-full-ml-lifecycle-for-auditable-scores.md)
* [Serve features through an online feature pipeline](0002-serve-features-through-an-online-feature-pipeline.md)
* [Expose scoring through a REST prediction microservice](0003-expose-scoring-through-a-rest-prediction-microservice.md)
* [Deploy the model as a real-time service](0004-deploy-the-model-as-a-real-time-service.md)
* [Use stateless horizontally scaled scoring instances](0005-use-stateless-horizontally-scaled-scoring-instances.md)
* [Scale scoring resources elastically](0006-scale-scoring-resources-elastically.md)
* [Monitor input and feature drift in production](0007-monitor-input-and-feature-drift-in-production.md)
* [Retrain when quality or data shifts cross thresholds](0008-retrain-when-quality-or-data-shifts-cross-thresholds.md)

## Decisions left open

* Model family and fraud-scoring algorithm selection
* Explanation method and how explanations are retained per score
* Fallback behavior when scoring or feature retrieval is unavailable
* Latency budget allocation and hard timeout behavior
* Authentication, authorization, encryption, and retention policies
* Training-data labeling and feedback process
