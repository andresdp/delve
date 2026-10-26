# Central training pipeline

*Where should model training run?*

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly from newly labelled images, while inference runs on cameras. The brief gives no indication that training must happen on the production devices.

## Decision Drivers

* weekly retraining
* small team
* tight budget

## Considered Options

* Central training pipeline
* Train on production devices

## Decision Outcome

Chosen option: "Central training pipeline".

A shared pipeline fits weekly retraining better than coordinating training across production cameras, though its hosting details remain open.

### Consequences

* Newly labelled images must be available to the training pipeline.
* Training requires some centralized compute and storage.

## Pros and Cons of the Options

### Central training pipeline

* Good, because shared compute
* Good, because consistent process
* Bad, because training infrastructure cost
* Bad, because image collection needed

### Train on production devices

* Good, because local data access
* Good, because no central training service
* Bad, because device resource contention
* Bad, because complex fleet coordination
