# Persist and provide features through a feature store

* System: Card-fraud scoring service

## Context and Problem Statement

The system must identify the features used for each score later; the brief does not specify a feature persistence mechanism.

## Decision Drivers

* Feature traceability
* Auditor review
* Score reproducibility

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

A dedicated feature store is the closer fit for consistently identifying the features behind each score, though the design space gives no source evidence for this choice (d:4, v:4.1).

### Consequences

* Feature values must be associated with scored transactions.
* This choice does not itself define audit retention or access controls.

## Pros and Cons of the Options

### Feature store

* Good, because Dedicated feature access
* Bad, because Feature-store operation required
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Uses general data stores
* Bad, because Feature access is not specialized
* Sources: `d:4`, `v:4.2`
