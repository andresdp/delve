# Data-to-model lineage management

*How should model versions and score lineage be recorded?*

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to identify which model version and features produced every score. The design space includes linking dataset versions and profiles to training context, model metadata, and deployment status.

## Decision Drivers

* Auditability: model version
* Auditability: feature provenance

## Considered Options

* Data-to-model lineage management (`v:20.4`)
* Model artifact and dependency versioning (`v:20.2`)

## Decision Outcome

Chosen option: "Data-to-model lineage management" (`v:20.4`).

Auditability decides the choice: linking dataset and training context to model metadata better supports tracing both the deployed version and its feature provenance. This requires additional metadata capture and retention.

### Consequences

* Record model, dataset, feature, and deployment identifiers for each scoring release.
* Retain lineage metadata for the audit period.

## Pros and Cons of the Options

### Data-to-model lineage management

* Good, because Auditability: links datasets to model metadata
* Good, because Reproducibility: records training context
* Bad, because Cost: requires metadata capture
* Bad, because Availability: incomplete lineage weakens audit trail
* Sources: `s10_p08`, `s20_p03`, `s20_p05`, `s20_p08`

### Model artifact and dependency versioning

* Good, because Auditability: identifies deployed model artifact
* Good, because Reproducibility: tracks model dependencies
* Bad, because Auditability: feature lineage may be absent
* Bad, because Cost: requires version management
