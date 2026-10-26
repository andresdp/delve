# Validate models before fleet rollout

* System: On-device visual inspection

## Context and Problem Statement

A new model replaces the current defect detector on production devices. A staged rollout limits exposure if a weekly model is faulty.

## Decision Drivers

* Detection quality
* Offline operation
* Low infrastructure cost

## Considered Options

* Validate then stage rollout
* Push each trained model fleet-wide

## Decision Outcome

Chosen option: "Validate then stage rollout".

Detection quality decides the choice: test and staged rollout reduce the impact of regressions. This gives up the speed and operational simplicity of an immediate fleet-wide push.

### Consequences

* Keep a known-good model available for recovery.
* Define validation criteria and rollout stages.

## Pros and Cons of the Options

### Validate then stage rollout

* Good, because Detection quality: catches regressions before broad release
* Good, because Offline operation: allows gradual installation as devices connect
* Bad, because Infrastructure cost: adds validation and rollout steps

### Push each trained model fleet-wide

* Good, because Weekly model freshness: fastest broad deployment
* Bad, because Detection quality: errors affect the whole fleet
* Bad, because Low infrastructure cost: failures can create production disruption
