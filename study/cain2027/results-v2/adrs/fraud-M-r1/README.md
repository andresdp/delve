# Architecture decisions: Card-fraud scoring service

* [prediction mode](0001-prediction-mode.md)
* [scoring interface](0002-scoring-interface.md)
* [serving capacity under peaks](0003-serving-capacity-under-peaks.md)
* [model and feature audit trail](0004-model-and-feature-audit-trail.md)

## Not grounded in the design space

* Model family and fraud decision threshold; the brief does not specify accuracy targets, error costs, or authorization policy.
* Feature retrieval and storage design, including online/offline feature consistency.
* Prediction fallback behavior when the model or feature dependencies are unavailable.
* Monitoring and alerting thresholds, retraining triggers, and model promotion controls.
* Audit record retention duration, access controls, and privacy requirements.
* Concrete protocol choice, traffic profile, deployment infrastructure, and latency measurement target within the stated tens of milliseconds.
