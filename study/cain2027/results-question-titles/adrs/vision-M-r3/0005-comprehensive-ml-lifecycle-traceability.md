# Comprehensive ML lifecycle traceability

*How should model and training artifacts be tracked?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces successive models that must be associated with their training inputs and deployment state. The small team benefits from traceability when investigating regressions.

## Decision Drivers

* Weekly model versions
* Regression investigation
* Tight budget

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Artifact version control (`v:20.1`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

Choose lifecycle traceability to connect each weekly model to its data, training run, and deployment status. “MLOps Principles” and “Continuous Intelligence: Moving Machine Learning Application into Production Reliably” support this approach; the checked point was novel and unattested, so keep the implementation proportionate to the small team.

### Consequences

* Record dataset, training, model, and deployment identifiers.
* Integrated tracking adds operational setup and maintenance.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links data, runs, and models
* Good, because Tracks deployment health
* Bad, because More metadata to maintain
* Bad, because May exceed team capacity
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p06`

### Artifact version control

* Good, because Tracks deployable model artifacts
* Good, because Lower scope
* Bad, because Less lifecycle context
* Bad, because Weaker data-to-model lineage
* Sources: `s22_p03`
