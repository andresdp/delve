# Architecture decisions: Card-fraud scoring service

* [prediction serving mode](0001-prediction-serving-mode.md)
* [serving interface](0002-serving-interface.md)
* [serving state and scaling](0003-serving-state-and-scaling.md)
* [feature storage for online and training use](0004-feature-storage-for-online-and-training-use.md)
* [model and scoring lineage](0005-model-and-scoring-lineage.md)

## Not grounded in the design space

* Exact latency and availability objectives, including tail-latency targets and failure behavior.
* Feature definitions, source systems, and the per-score feature snapshot format.
* Audit retention, access control, and the required explainability method.
* Training cadence, fraud-label delay, model evaluation thresholds, and promotion policy.
* Chosen model family and concrete hosting infrastructure.
