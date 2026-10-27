# Train models weekly from newly labelled images

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained every week from newly labelled images. The small team and tight infrastructure budget favor a simple, scheduled training process.

## Decision Drivers

* Weekly retraining
* New labelled images
* Small team

## Considered Options

* Scheduled batch training
* Continuous retraining

## Decision Outcome

Chosen option: "Scheduled batch training".

A weekly batch cycle matches the brief's retraining cadence and keeps operations manageable for a small team.

### Consequences

* New labels may wait until the next cycle.
* Training runs need repeatable inputs and outputs.

## Pros and Cons of the Options

### Scheduled batch training

* Good, because Predictable process
* Good, because Simple operations
* Bad, because Updates wait for schedule
* Bad, because Needs a training job

### Continuous retraining

* Good, because Faster data feedback
* Good, because Frequent updates
* Bad, because More operational complexity
* Bad, because Higher infrastructure use
