# Persist score, model version, and feature snapshot

*How should each score be made auditable?*

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later determine which model version and features produced each score. The brief does not specify retention or privacy rules for transaction features.

## Decision Drivers

* Auditability
* Reproducibility

## Considered Options

* Persist score, model version, and feature snapshot
* Persist score and model version only
* Persist score and feature reference

## Decision Outcome

Chosen option: "Persist score, model version, and feature snapshot".

Auditability decides the choice because it directly preserves both required evidence points: model version and features. This gives up storage efficiency and requires feature data retention controls.

### Consequences

* Each scoring event creates a durable audit record.
* Feature snapshots increase storage and require access controls.

## Pros and Cons of the Options

### Persist score, model version, and feature snapshot

* Good, because Auditability: preserves inputs and model identity
* Bad, because Cost: stores per-transaction records

### Persist score and model version only

* Good, because Cost: stores less data
* Bad, because Reproducibility: original feature values unavailable

### Persist score and feature reference

* Good, because Cost: avoids duplicating feature values
* Bad, because Auditability: depends on referenced data retention
