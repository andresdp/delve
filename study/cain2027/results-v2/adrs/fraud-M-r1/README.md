# Architecture decisions: Card-fraud scoring service

* [Prediction mode](0001-prediction-mode.md)
* [Scoring interface](0002-scoring-interface.md)
* [Serving capacity under peaks](0003-serving-capacity-under-peaks.md)
* [Model and feature audit trail](0004-model-and-feature-audit-trail.md)

## Decisions left open

* Model family and fraud decision threshold; the brief does not specify accuracy targets, error costs, or authorization policy.
* Feature retrieval and storage design, including online/offline feature consistency.
* Prediction fallback behavior when the model or feature dependencies are unavailable.
* Monitoring and alerting thresholds, retraining triggers, and model promotion controls.
* Audit record retention duration, access controls, and privacy requirements.
* Concrete protocol choice, traffic profile, deployment infrastructure, and latency measurement target within the stated tens of milliseconds.
