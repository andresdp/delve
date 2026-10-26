# Architecture decisions: Large-scale document classification

* [prediction mode](0001-prediction-mode.md)
* [scaling for variable workload](0002-scaling-for-variable-workload.md)
* [classification result interface](0003-classification-result-interface.md)
* [detecting production quality drift](0004-detecting-production-quality-drift.md)
* [candidate model evaluation](0005-candidate-model-evaluation.md)
* [model and data traceability](0006-model-and-data-traceability.md)

## Not grounded in the design space

* Workflow execution coordination and orchestration (flagged as a prerequisite by the evaluation decision).
* Data retention, privacy, and access controls for insurance documents.
* Label acquisition and delay, evaluation metrics, and promotion thresholds.
* Consumer-specific delivery, availability, and freshness requirements.
* Model choice, including whether the LLM classifier is hosted or self-managed.
