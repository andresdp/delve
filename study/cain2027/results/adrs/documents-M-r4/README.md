# Architecture decisions: Large-scale document classification

* [prediction serving mode](0001-prediction-serving-mode.md)
* [scaling for seasonal volume](0002-scaling-for-seasonal-volume.md)
* [production quality and drift monitoring](0003-production-quality-and-drift-monitoring.md)
* [prediction delivery interface](0004-prediction-delivery-interface.md)

## Not grounded in the design space

* Data ingestion mechanism and source integration; the design-space relation says workflow coordination requires this decision first.
* Result schema, storage retention, and access control for the consuming teams.
* Ground-truth label collection and its delay, needed to define prediction-quality monitoring.
* Classification error costs, acceptance thresholds, and human review policy.
* Deployment platform, availability targets, and batch schedule.
