# Record the model version and feature snapshot for every score

* System: Card-fraud scoring service

## Context and Problem Statement

The audit requirement covers both the model version and the features used to produce each score.

## Decision Drivers

* Auditor explainability
* Feature attribution
* Historical reconstruction

## Considered Options

* Persist score with model and feature snapshot
* Persist score and model version only
* Recompute features from transaction history

## Decision Outcome

Chosen option: "Persist score with model and feature snapshot".

Persisting the exact inputs alongside the model identity provides the strongest evidence of what produced each score.

### Consequences

* Define a durable score record and retention policy
* Protect stored feature data with appropriate access controls

## Pros and Cons of the Options

### Persist score with model and feature snapshot

* Good, because Direct audit evidence
* Good, because Reconstructs scoring inputs
* Bad, because Storage and write overhead
* Bad, because Sensitive data controls needed

### Persist score and model version only

* Good, because Lower storage cost
* Good, because Simpler logging
* Bad, because Cannot establish used features
* Bad, because Limited explanation later

### Recompute features from transaction history

* Good, because Smaller score records
* Good, because Uses existing history
* Bad, because Historical inputs may change
* Bad, because Recomputation may diverge
