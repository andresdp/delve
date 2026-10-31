# Retrain the model weekly from newly labelled images

* System: On-device visual inspection

## Context and Problem Statement

The model must incorporate newly labelled images on a weekly cadence. The brief does not identify the training infrastructure or where those images are stored.

## Decision Drivers

* Weekly retraining
* New labelled images
* Tight budget

## Considered Options

* Central batch training
* Train on each device

## Decision Outcome

Chosen option: "Central batch training".

A shared weekly training process is a practical fit for a small team and tight infrastructure budget, provided labelled images can be collected centrally.

### Consequences

* Training requires access to the labelled images.
* Training capacity and cadence must support weekly runs.

## Pros and Cons of the Options

### Central batch training

* Good, because Shared compute
* Good, because Centralized training process
* Bad, because Images must reach training site
* Bad, because Requires training infrastructure

### Train on each device

* Good, because Images stay local
* Good, because No central image transfer
* Bad, because Consumes device resources
* Bad, because Harder to coordinate
