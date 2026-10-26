# How should model installation handle failures?

* System: On-device visual inspection

## Context and Problem Statement

Models are pushed to devices that may lack reliable connectivity, so an update can be interrupted or prove unusable.

## Decision Drivers

* Offline devices
* Weekly updates
* Production inspection

## Considered Options

* Stage, verify, then activate with rollback
* Replace the active model in place

## Decision Outcome

Chosen option: "Stage, verify, then activate with rollback".

Keeping the current model until the replacement is verified protects inspection from interrupted downloads or unusable updates.

### Consequences

* Devices need temporary storage for another model copy.
* The update process must define verification and rollback behavior.

## Pros and Cons of the Options

### Stage, verify, then activate with rollback

* Good, because Preserves working model
* Good, because Detects incomplete updates
* Bad, because Needs local version storage
* Bad, because Adds update logic

### Replace the active model in place

* Good, because Simple installation flow
* Good, because Less local storage
* Bad, because Interrupted update risk
* Bad, because Recovery may need intervention
