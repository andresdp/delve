# Architecture decisions: Card-fraud scoring service

* [Score transactions synchronously before authorization](0001-score-transactions-synchronously-before-authorization.md)
* [Scale the scoring service to sustain peak traffic](0002-scale-the-scoring-service-to-sustain-peak-traffic.md)
* [Record model version and scoring features for each score](0003-record-model-version-and-scoring-features-for-each-score.md)
* [Keep model versions identifiable and selectable](0004-keep-model-versions-identifiable-and-selectable.md)

## Decisions left open

* Feature definitions, sources, and freshness requirements.
* Audit record retention period, access controls, and storage location.
* Required availability target and recovery objectives.
* Behavior when scoring is unavailable or exceeds its latency budget.
* Model training, validation, approval, and rollout process.
* Deployment platform, capacity limits, and peak traffic profile.
