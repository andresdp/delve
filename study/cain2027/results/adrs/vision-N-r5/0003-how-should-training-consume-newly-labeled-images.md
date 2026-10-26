# How should training consume newly labeled images?

* System: On-device visual inspection

## Context and Problem Statement

Newly labeled images feed a weekly retraining cycle. The brief does not specify a data store or training platform, so the design should keep these concerns modest and separable.

## Decision Drivers

* Weekly retraining
* New labeled images
* Tight budget

## Considered Options

* Scheduled batch training from a shared image and label store
* Continuous training on each new label

## Decision Outcome

Chosen option: "Scheduled batch training from a shared image and label store".

A weekly batch aligns with the stated retraining cadence and limits operational overhead for a small team.

### Consequences

* Training inputs and labels need versioning.
* Model releases follow the weekly training schedule.

## Pros and Cons of the Options

### Scheduled batch training from a shared image and label store

* Good, because Simple weekly workflow
* Good, because Auditable inputs
* Bad, because Needs shared storage
* Bad, because Batch feedback cycle

### Continuous training on each new label

* Good, because Faster feedback
* Good, because Frequent model updates
* Bad, because More operational complexity
* Bad, because Harder release control
