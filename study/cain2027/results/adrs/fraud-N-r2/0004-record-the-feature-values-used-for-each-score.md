# Record the feature values used for each score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditability requires identifying which features produced a score, including the values supplied to the model at scoring time.

## Decision Drivers

* Feature attribution
* Auditability

## Considered Options

* Persist scoring-time feature snapshot
* Persist feature names only

## Decision Outcome

Chosen option: "Persist scoring-time feature snapshot".

A snapshot preserves the actual feature inputs used, rather than only describing the feature set.

### Consequences

* Feature snapshots must be linked to the transaction score.
* Storage and access controls must account for feature data.

## Pros and Cons of the Options

### Persist scoring-time feature snapshot

* Good, because Preserves exact inputs
* Good, because Supports later review
* Bad, because Increases storage volume

### Persist feature names only

* Good, because Smaller audit records
* Bad, because Cannot establish input values
