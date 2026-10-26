# Validate, stage, and retain a rollback version

*How should model releases be promoted?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining creates frequent candidate models, while production inspection depends on the deployed model. The brief does not describe validation or rollback practices.

## Decision Drivers

* Weekly retraining
* Small team
* Offline operation

## Considered Options

* Automatically replace the deployed model
* Validate, stage, and retain a rollback version

## Decision Outcome

Chosen option: "Validate, stage, and retain a rollback version".

Offline operation decides the choice: a device needs a usable local model even if an update fails. This gives up some weekly release speed and requires a validation and rollback process.

### Consequences

* Devices need storage for the current and previous model.
* Promotion criteria and rollback triggers must be defined.

## Pros and Cons of the Options

### Automatically replace the deployed model

* Good, because Weekly retraining: minimal promotion delay
* Good, because Small team: fewer manual release steps
* Bad, because Offline operation: failures may remain until reconnection
* Bad, because Weekly retraining: unvalidated regressions can reach devices

### Validate, stage, and retain a rollback version

* Good, because Offline operation: device can keep a working local version
* Good, because Weekly retraining: separates candidates from releases
* Bad, because Small team: validation and rollout process to maintain
* Bad, because Tight infrastructure budget: retain extra model copies
