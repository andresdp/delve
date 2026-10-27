# Retrain the model centrally on newly labelled images

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly using newly labelled images, while the team has limited infrastructure budget. Central training avoids requiring training hardware on every production device.

## Decision Drivers

* Weekly retraining
* Small team
* Tight budget

## Considered Options

* Central training pipeline
* Train on each device

## Decision Outcome

Chosen option: "Central training pipeline".

A shared pipeline fits a weekly cadence and avoids duplicating training work across the fleet.

### Consequences

* New labelled images must reach the training environment.
* Training infrastructure and dataset handling need ownership.

## Pros and Cons of the Options

### Central training pipeline

* Good, because Shared compute
* Good, because One training workflow
* Bad, because Needs image transfer
* Bad, because Requires training infrastructure

### Train on each device

* Good, because Local data stays local
* Good, because No central training service
* Bad, because Repeated compute cost
* Bad, because Hard to coordinate
