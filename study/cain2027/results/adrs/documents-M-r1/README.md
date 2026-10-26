# Architecture decisions: Large-scale document classification

* [production quality and drift monitoring](0001-production-quality-and-drift-monitoring.md)
* [prediction serving mode](0002-prediction-serving-mode.md)
* [runtime capacity scaling](0003-runtime-capacity-scaling.md)

## Not grounded in the design space

* How teams authenticate to and access shared classification results.
* The required freshness or latency for each consuming team.
* How labels are collected and how drift alerts are escalated or approved for action.
