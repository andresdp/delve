# Model and scoring lineage

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later identify the model version and features behind each score, requiring versioned artifacts and linked scoring metadata.

## Decision Drivers

* Auditor traceability
* Model version identification
* Feature identification

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Choose lifecycle traceability because artifact versioning alone does not capture which features produced an individual score. The design space identifies this value as covering artifact, run, metadata, and dataset traceability, but no passage identifiers were retrieved for these alternatives.

### Consequences

* Each score must retain model and feature references.
* Metadata capture adds storage and processing work.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts, runs, and datasets
* Good, because Includes deployment health tracking
* Bad, because Requires broad metadata capture
* Bad, because Implementation detail is unspecified

### Artifact version control

* Good, because Versions models and dependencies
* Good, because Supports reproducible deployment
* Bad, because Does not alone link score inputs
* Bad, because Narrower lifecycle coverage
