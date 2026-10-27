# Retrain models in a centralized weekly pipeline

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for weekly retraining, while the devices are intended to perform inference. A shared training pipeline fits the small team and constrained infrastructure budget.

## Decision Drivers

* Weekly retraining
* New labelled images
* Small team
* Tight budget

## Considered Options

* Centralized scheduled training
* Train separately on devices

## Decision Outcome

Chosen option: "Centralized scheduled training".

A single weekly pipeline is easier for a small team to operate and avoids coordinating training across production devices.

### Consequences

* Training needs access to the newly labelled images.
* Compute demand concentrates in the training environment.

## Pros and Cons of the Options

### Centralized scheduled training

* Good, because One training workflow
* Good, because Shared compute
* Bad, because Training depends on data upload
* Bad, because Central compute required

### Train separately on devices

* Good, because Local data use
* Good, because Less central compute
* Bad, because Fleet coordination burden
* Bad, because Inconsistent training runs
