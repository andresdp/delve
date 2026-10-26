# Architecture decisions: Large-scale document classification

* [how should classifications be computed and delivered](0001-how-should-classifications-be-computed-and-delivered.md)
* [how should compute capacity handle seasonal variation](0002-how-should-compute-capacity-handle-seasonal-variation.md)
* [how should consuming teams access classifications](0003-how-should-consuming-teams-access-classifications.md)
* [how should production quality drift be detected](0004-how-should-production-quality-drift-be-detected.md)

## Not grounded in the design space

* How labels are produced and how often they become available.
* Whether and when detected drift should trigger retraining or human review.
* Required latency, freshness, availability, and seasonal peak capacity targets.
* Classification result retention, access control, and privacy requirements.
* The schema, delivery mechanism, and ownership expectations for each consuming team.
