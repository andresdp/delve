# Record model version and scoring features for each score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later identify the model version and features used to produce each score.

## Decision Drivers

* Auditability
* Model traceability

## Considered Options

* Persist score, model version, and feature snapshot
* Persist score and model version only
* Persist score and feature snapshot only

## Decision Outcome

Chosen option: "Persist score, model version, and feature snapshot".

This records both items the brief explicitly requires auditors to recover for every score.

### Consequences

* A durable per-score audit record is needed.
* Feature snapshots increase storage and data-governance obligations.

## Pros and Cons of the Options

### Persist score, model version, and feature snapshot

* Good, because Direct decision reconstruction
* Good, because Explicit audit evidence
* Bad, because Storage and retention cost
* Bad, because Feature data needs protection

### Persist score and model version only

* Good, because Lower storage cost
* Good, because Simpler data handling
* Bad, because Cannot identify input features later

### Persist score and feature snapshot only

* Good, because Feature evidence retained
* Good, because No model registry dependency
* Bad, because Cannot identify model version
