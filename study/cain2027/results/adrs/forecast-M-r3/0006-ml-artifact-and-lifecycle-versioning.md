# ML artifact and lifecycle versioning

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts for past weeks must be reproducible, so the system needs to link prior inputs and model artifacts to their training context.

## Decision Drivers

* Past-week reproducibility
* Auditability
* Fast model iteration

## Considered Options

* Data-to-model lineage management (`v:20.4`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Data-to-model lineage management" (`v:20.4`).

Linking dataset versions with training context and model metadata best supports reproducing a past week’s forecast; practitioner sources include “Architecting a Machine Learning System for Risk” and “MLOps: Methods and Tools of DevOps for Machine Learning.”

### Consequences

* Input snapshots and model versions must be retained.
* Each run needs captured lineage metadata.

## Pros and Cons of the Options

### Data-to-model lineage management

* Good, because Links data and model versions
* Good, because Supports reproducible context
* Bad, because Metadata capture effort
* Bad, because Requires versioned datasets
* Sources: `s10_p08`, `s20_p03`, `s20_p05`

### Artifact version control

* Good, because Tracks model dependencies
* Good, because Enables artifact reuse
* Bad, because Narrow lifecycle coverage
* Bad, because Does not alone link data
