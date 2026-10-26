# Preserve data for historical replay

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts must be reproducible for any past week, so the system needs to retain the inputs and their provenance. The design space supports preserving original data and tracing how it was processed.

## Decision Drivers

* Past-week reproducibility
* Weekly run stability

## Considered Options

* Traceable and preserved data (`v:42.1`)
* Cataloged data (`v:42.2`)

## Decision Outcome

Chosen option: "Traceable and preserved data" (`v:42.1`).

Past-week reproducibility decides the choice: retained, traceable inputs make historical reconstruction possible. Sources including “Architecting a Machine Learning Pipeline” describe provenance and data preservation; this adds storage and tracking work.

### Consequences

* Retain immutable input snapshots and provenance.
* Historical runs need references to the appropriate snapshots.

## Pros and Cons of the Options

### Traceable and preserved data

* Good, because Reproducibility: recover original inputs and processing history
* Bad, because Weekly run stability: requires retained data and provenance
* Sources: `s02_p04`, `s02_p05`, `s02_p06`, `s10_p08`

### Cataloged data

* Good, because Reproducibility: records dataset versions and metadata
* Bad, because Past-week reproducibility: cataloging alone does not preserve original data
* Sources: `s02_p04`
