# Architecture decisions: Large-scale document classification

* [Production quality and drift monitoring](0001-production-quality-and-drift-monitoring.md)
* [Prediction serving mode](0002-prediction-serving-mode.md)
* [Runtime capacity scaling](0003-runtime-capacity-scaling.md)

## Decisions left open

* How teams authenticate to and access shared classification results.
* The required freshness or latency for each consuming team.
* How labels are collected and how drift alerts are escalated or approved for action.
