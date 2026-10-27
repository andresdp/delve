# Architecture decisions: Large-scale document classification

* [Prediction mode](0001-prediction-mode.md)
* [Scaling for variable workload](0002-scaling-for-variable-workload.md)
* [Classification result interface](0003-classification-result-interface.md)
* [Detecting production quality drift](0004-detecting-production-quality-drift.md)
* [Candidate model evaluation](0005-candidate-model-evaluation.md)
* [Model and data traceability](0006-model-and-data-traceability.md)

## Decisions left open

* Workflow execution coordination and orchestration (flagged as a prerequisite by the evaluation decision).
* Data retention, privacy, and access controls for insurance documents.
* Label acquisition and delay, evaluation metrics, and promotion thresholds.
* Consumer-specific delivery, availability, and freshness requirements.
* Model choice, including whether the LLM classifier is hosted or self-managed.
