# Retrain models on a weekly batch cadence

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained every week from newly labelled images. A batch workflow fits this cadence and avoids requiring a continuously available training pipeline.

## Decision Drivers

* Weekly retraining
* Small team
* Tight infrastructure budget

## Considered Options

* Weekly batch training
* Continuous training

## Decision Outcome

Chosen option: "Weekly batch training".

A weekly batch aligns directly with the required retraining interval while limiting operational and infrastructure overhead.

### Consequences

* Training and release become weekly operational steps.
* New labels may wait until the next batch.

## Pros and Cons of the Options

### Weekly batch training

* Good, because Matches stated cadence
* Good, because Simple orchestration
* Bad, because Updates wait for batch
* Bad, because Training failures delay release

### Continuous training

* Good, because Faster incorporation
* Good, because Frequent model refresh
* Bad, because More operational complexity
* Bad, because Higher infrastructure demand
