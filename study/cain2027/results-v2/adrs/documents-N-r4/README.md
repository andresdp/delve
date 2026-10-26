# Architecture decisions: Large-scale document classification

* [how should classification work scale with demand](0001-how-should-classification-work-scale-with-demand.md)
* [how should classification results reach consuming teams](0002-how-should-classification-results-reach-consuming-teams.md)
* [how should the system expose quality drift](0003-how-should-the-system-expose-quality-drift.md)
* [how should model changes be deployed and attributed](0004-how-should-model-changes-be-deployed-and-attributed.md)

## Not grounded in the design space

* Classification result latency target or freshness SLO.
* Cost limits and compute budget.
* Security, privacy, regulatory, and document retention requirements.
* How ground-truth labels are obtained and who reviews sampled cases.
* Required availability, recovery, and data-loss targets.
* Result schema, consumer delivery guarantees, and event retention.
