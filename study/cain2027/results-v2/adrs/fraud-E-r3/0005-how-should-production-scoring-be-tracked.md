# How should production scoring be tracked?

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need a later account of the inputs and model that produced each score.

## Decision Drivers

* Auditability
* Peak availability

## Considered Options

* Model in-production tracking (`v:22.4`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model in-production tracking" (`v:22.4`).

Auditability decides: tracking inputs and outputs most directly supports explaining a score later. We accept the added storage and processing work, keeping it off the synchronous scoring path where possible.

### Consequences

* Persist model version, feature identity or values, and score together.
* Set retention and access controls for audit records.

## Pros and Cons of the Options

### Model in-production tracking

* Good, because Auditability: tracks inputs, outputs, and usage
* Bad, because Peak availability: tracking adds storage and processing load
* Sources: `d:22`, `v:22.4`

### Monitoring or logging data and predictions

* Good, because Peak availability: operational signals aid response
* Bad, because Auditability: may omit required lineage detail
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Bad, because Auditability: no production record
* Sources: `d:22`, `v:22.3`
