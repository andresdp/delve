# Architecture decisions: Large-scale document classification

* [how should documents enter classification](0001-how-should-documents-enter-classification.md)
* [how should classifier capacity scale](0002-how-should-classifier-capacity-scale.md)
* [how should teams consume classifications](0003-how-should-teams-consume-classifications.md)
* [how should classification quality drift be monitored](0004-how-should-classification-quality-drift-be-monitored.md)

## Not grounded in the design space

* Document formats, sizes, and privacy or retention constraints
* Required classification latency and availability targets
* Claim type taxonomy and confidence or escalation policy
* Model provider, hosting, versioning, and fallback strategy
* Consumer access patterns, delivery guarantees, and result retention
* Availability and freshness of labeled evaluation data; drift alert thresholds and response process
