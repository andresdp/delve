# Architecture decisions: Large-scale document classification

* [prediction serving mode](0001-prediction-serving-mode.md)
* [runtime capacity scaling](0002-runtime-capacity-scaling.md)
* [production quality and drift monitoring](0003-production-quality-and-drift-monitoring.md)

## Not grounded in the design space

* Prediction freshness or response-time target and batch scoring cadence.
* How results are exposed to several consuming teams, including interface and access controls.
* LLM provider, model selection, prompt and model versioning, and fallback behavior.
* Document retention, privacy, security, and audit requirements.
* Label availability and delay, drift thresholds, and retraining or remediation policy.
* Seasonal peak rates, cost ceiling, and deployment infrastructure.
