# Central batch training

*How should training run?*

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for weekly retraining, while the team and infrastructure budget are limited. Training can be managed centrally or separately across devices.

## Decision Drivers

* Weekly retraining
* New labels
* Tight budget

## Considered Options

* Central batch training
* Train on devices

## Decision Outcome

Chosen option: "Central batch training".

A single weekly batch workflow fits the stated retraining cadence and small team better than coordinating training across production devices. It implies that labelled images must be accessible to the training environment.

### Consequences

* A central dataset and training environment are required.
* Image transfer and storage costs depend on data volume.

## Pros and Cons of the Options

### Central batch training

* Good, because One training workflow
* Good, because Consistent model artifact
* Bad, because Needs training infrastructure
* Bad, because Requires image collection

### Train on devices

* Good, because Images can stay local
* Good, because Uses device data
* Bad, because Device resource limits
* Bad, because Fleet training complexity
