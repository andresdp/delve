# Architecture decisions: On-device visual inspection

* [Model inference placement](0001-model-inference-placement.md)
* [Retraining schedule](0002-retraining-schedule.md)
* [Retraining execution](0003-retraining-execution.md)
* [Training compute scaling](0004-training-compute-scaling.md)
* [Model release strategy](0005-model-release-strategy.md)
* [Model and training lineage](0006-model-and-training-lineage.md)
* [Production monitoring and retraining feedback](0007-production-monitoring-and-retraining-feedback.md)

## Decisions left open

* Main requirements, ranked: inference without network access; weekly retraining and device rollout; tight infrastructure budget; small-team operating effort. The brief provides no latency target, dataset volume or retention policy, model framework, device update protocol, or failure and rollback service-level targets.
* The design point check returned no adopting sources for the selected combination. A rival point swapping in model-as-a-service deployment, unified release automation, artifact-only versioning, parallel candidate training, and manual retraining also had no adopting sources. The selected point warned that it combines three values within Production Monitoring and Adaptation; that dimension has zero exclusivity in the workspace, so the monitoring practices are treated as combinable.
