# Managed cloud training

*How should models be retrained?*

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images, but the brief does not specify where training runs or how data is collected.

## Decision Drivers

* Weekly retraining
* Tight infrastructure budget
* Small team

## Considered Options

* Managed cloud training
* Self-managed training infrastructure
* Train on production devices

## Decision Outcome

Chosen option: "Managed cloud training".

Weekly retraining and the small team favor managed compute that can be used on a schedule. This accepts recurring service costs, whose level is not specified in the brief.

### Consequences

* Training depends on access to the chosen service.
* Image transfer, retention, and training costs need limits.

## Pros and Cons of the Options

### Managed cloud training

* Good, because Small team: less training infrastructure to operate
* Good, because Weekly retraining: provision compute when needed
* Bad, because Tight infrastructure budget: recurring service and storage costs

### Self-managed training infrastructure

* Good, because Tight infrastructure budget: reuses owned compute
* Bad, because Small team: infrastructure upkeep
* Bad, because Weekly retraining: capacity management burden

### Train on production devices

* Good, because Tight infrastructure budget: no separate training fleet
* Bad, because Weekly retraining: competes with inspection workload
* Bad, because Small team: device training support
