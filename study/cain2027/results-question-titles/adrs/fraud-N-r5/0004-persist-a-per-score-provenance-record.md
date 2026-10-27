# Persist a per-score provenance record

*How should score provenance be captured?*

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later be able to identify the model version and features that produced each score.

## Decision Drivers

* Auditor traceability
* Model version
* Scoring features

## Considered Options

* Persist a per-score provenance record
* Retain aggregate service logs

## Decision Outcome

Chosen option: "Persist a per-score provenance record".

A record linked to each score can capture the model version and features needed for later audit.

### Consequences

* Scoring writes add work to the request path.
* Records require retention and access policies.

## Pros and Cons of the Options

### Persist a per-score provenance record

* Good, because Direct score-to-input trace
* Good, because Supports later review
* Bad, because Storage and write overhead
* Bad, because Feature data needs protection

### Retain aggregate service logs

* Good, because Lower storage burden
* Good, because Operationally familiar
* Bad, because Weak per-score linkage
* Bad, because May omit feature values
