# Record the feature values used for each score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify which features produced a score, not only which model was used.

## Decision Drivers

* Feature traceability
* Auditability

## Considered Options

* Persist a per-score feature snapshot
* Persist feature names only

## Decision Outcome

Chosen option: "Persist a per-score feature snapshot".

Keeping the values supplied to the model alongside its version provides an auditable record of the inputs that produced each score.

### Consequences

* Scoring records include feature values and require storage.

## Pros and Cons of the Options

### Persist a per-score feature snapshot

* Good, because Shows values used at scoring time
* Good, because Supports later review
* Bad, because Adds storage and write load
* Bad, because Requires retention controls

### Persist feature names only

* Good, because Lower storage use
* Good, because Simpler records
* Bad, because Does not show values used
* Bad, because Harder to reconstruct a score
