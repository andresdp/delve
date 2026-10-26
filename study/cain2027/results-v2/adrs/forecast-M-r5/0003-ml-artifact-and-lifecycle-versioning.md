# ML artifact and lifecycle versioning

* System: Retail demand forecasting

## Context and Problem Statement

Reproducing any past week requires recovering the data, pipeline, dependencies, and model used for its forecast. Model ideas also need comparable experiment records.

## Decision Drivers

* Reproduce past weeks
* Fast production changes

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Reproducing past weeks decides: comprehensive traceability includes dataset versions, training runs, artifacts, and deployment status, with higher metadata overhead. “MLOps Principles” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support integrated lifecycle tracking; the checked point has no warnings but is unattested as a complete combination.

### Consequences

* Record input dataset versions, pipeline revisions, dependencies, and model artifacts per run.
* Lifecycle metadata adds work to the small team.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Reproducibility: links data, runs, and artifacts
* Good, because Fast production changes: compares experiments
* Bad, because Small team: more metadata to maintain
* Sources: `s08_p01`, `s22_p03`, `s22_p04`

### Pipeline and experiment version control

* Good, because Fast production changes: compares configurations
* Bad, because Reproducibility: less lifecycle coverage
* Sources: `s04_p01`, `s04_p05`
