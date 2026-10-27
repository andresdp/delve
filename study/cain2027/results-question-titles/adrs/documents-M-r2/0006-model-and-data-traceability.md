# Model and data traceability

* System: Large-scale document classification

## Context and Problem Statement

Drift investigations and safe updates benefit from linking deployed models to their training data and runs. Multiple teams also need reproducible classification behavior.

## Decision Drivers

* Drift investigation
* Reproducible updates
* Shared operation

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Comprehensive traceability best supports explaining drift and reproducing candidate updates across teams. “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” and “MLOps Principles” document end-to-end lifecycle records; the checked point was unattested.

### Consequences

* Record dataset, pipeline, run, model, and deployment metadata.
* Teams take on additional tracking and governance work.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links data, runs, and models
* Good, because Tracks deployment health
* Bad, because Adds governance work
* Sources: `s08_p01`, `s22_p03`, `s22_p04`

### Artifact version control

* Good, because Versions model assets
* Good, because Supports reuse
* Bad, because Less lifecycle context
* Sources: `s22_p03`
