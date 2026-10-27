# Comprehensive ML lifecycle traceability

*How should past forecasts and training runs be reproduced?*

* System: Retail demand forecasting

## Context and Problem Statement

The system must reproduce forecasts for any past week, which requires retaining the model and the inputs and configuration used to produce each result.

## Decision Drivers

* historical reproducibility
* auditability
* experiment comparison

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

This choice covers dataset versions, pipeline definitions, artifacts, runs, and deployment status needed to reproduce a past week. “MLOps Principles” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support lifecycle traceability; the checked design point selected this value, while a simpler artifact-versioning rival offered less coverage.

### Consequences

* Record dataset and code versions for each run.
* Persist run parameters and output metadata.
* Maintain a traceable model promotion history.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because links data and models
* Good, because supports run reconstruction
* Bad, because metadata overhead
* Bad, because more governance work
* Sources: `s08_p01`, `s22_p03`, `s22_p06`

### Pipeline and experiment version control

* Good, because compares experiments
* Good, because versions pipeline and artifacts
* Bad, because less complete lineage
* Bad, because dataset linkage may be missing
* Sources: `s04_p01`, `s04_p03`, `s17_p03`
