# Track complete lifecycle lineage for reproducible forecasts

* System: Retail demand forecasting

## Context and Problem Statement

The system must reproduce forecasts for any past week, which requires recovering the data, pipeline, artifacts, and training context for that run.

## Decision Drivers

* Past-week reproducibility
* Run traceability
* Small team

## Considered Options

* Artifact version control (`v:20.1`)
* Comprehensive ML lifecycle traceability (`v:20.3`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

This accepted value covers dataset versions, training runs, pipeline designs, artifacts, and deployment health. “MLOps Principles” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support lifecycle traceability; the point check found no attested source combination, so this is a reasoned selection rather than a documented end-to-end pattern.

### Consequences

* Retain dataset and run metadata for each forecast week.
* The team must keep lineage records complete.

## Pros and Cons of the Options

### Artifact version control

* Good, because Versions model assets
* Good, because Supports reuse
* Bad, because Limited run context
* Bad, because Limited dataset lineage

### Comprehensive ML lifecycle traceability

* Good, because Links data and runs
* Good, because Tracks pipeline and model health
* Bad, because More metadata to manage
* Bad, because Requires lifecycle discipline
* Sources: `s08_p01`, `s22_p03`, `s22_p08`
