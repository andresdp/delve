# Record score-time model and feature inputs

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to establish which model version and which features produced each score. Retaining the score-time inputs preserves that evidence if models or feature sources later change.

## Decision Drivers

* Auditor explainability
* Reproducibility

## Considered Options

* Persist model version and feature values with each score
* Persist model version and recompute features later

## Decision Outcome

Chosen option: "Persist model version and feature values with each score".

Auditor explainability decides this choice: the actual score-time inputs and model version provide direct evidence of how the score was produced. This gives up storage cost and requires managing retained records.

### Consequences

* Each score requires a durable record of its model version and feature values.
* Retention and access controls for these records need definition.

## Pros and Cons of the Options

### Persist model version and feature values with each score

* Good, because Explainability: retain the inputs used for the score
* Good, because Reproducibility: identify the scoring model version
* Bad, because Cost: store a record for every score

### Persist model version and recompute features later

* Good, because Cost: store fewer feature values
* Bad, because Reproducibility: later feature sources may differ
* Bad, because Explainability: historical inputs may be unavailable
