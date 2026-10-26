# Update devices using staged, rollback-capable releases

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining means models change regularly, while production devices may be offline or have limited connectivity. Staging and rollback reduce the impact of a problematic release.

## Decision Drivers

* Weekly model updates
* Network independence
* Small team

## Considered Options

* Staged rollout with rollback
* Replace the model on all devices at once

## Decision Outcome

Chosen option: "Staged rollout with rollback".

Weekly model updates decide for a controlled rollout: it limits the impact of a bad model and permits recovery. The trade-off is extra release tracking and slower completion across offline devices.

### Consequences

* Devices need a way to retain or restore a prior model.
* Update status may differ across the fleet.

## Pros and Cons of the Options

### Staged rollout with rollback

* Good, because Weekly model updates: controlled release progression
* Good, because Small team: limits fleet-wide failures
* Bad, because Network independence: rollout may take time
* Bad, because Small team: requires release state tracking

### Replace the model on all devices at once

* Good, because Small team: simple rollout flow
* Bad, because Weekly model updates: broad impact if a release fails
* Bad, because Network independence: offline devices remain out of sync
