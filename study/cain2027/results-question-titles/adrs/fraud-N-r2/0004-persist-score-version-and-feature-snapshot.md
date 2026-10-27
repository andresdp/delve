# Persist score, version, and feature snapshot

*What should be retained for audit explanation?*

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires later explanation of which features produced a score, as well as which model version was used. A durable record must connect each score to those inputs.

## Decision Drivers

* Auditor review
* Feature provenance
* Model provenance

## Considered Options

* Persist score, version, and feature snapshot
* Persist score and version only

## Decision Outcome

Chosen option: "Persist score, version, and feature snapshot".

Retaining the feature snapshot alongside the score and model version directly supports later identification of the inputs that produced it.

### Consequences

* Audit records require durable storage and retention rules.
* Feature snapshots increase storage and data-governance needs.

## Pros and Cons of the Options

### Persist score, version, and feature snapshot

* Good, because Reconstructs scoring inputs
* Good, because Supports later audit
* Bad, because Storage and retention cost
* Bad, because Feature data needs protection

### Persist score and version only

* Good, because Smaller records
* Good, because Simpler retention
* Bad, because Cannot identify used features
* Bad, because Insufficient for stated audit need
