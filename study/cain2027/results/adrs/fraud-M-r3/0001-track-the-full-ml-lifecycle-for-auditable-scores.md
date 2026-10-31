# Track the full ML lifecycle for auditable scores

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors need to trace each score to its model version and features. Lifecycle metadata can connect deployed models with training runs and datasets.

## Decision Drivers

* Audit trail
* Model versioning
* Feature lineage

## Considered Options

* Comprehensive ML lifecycle traceability (`v:20.3`)
* Pipeline and experiment version control (`v:20.2`)

## Decision Outcome

Chosen option: "Comprehensive ML lifecycle traceability" (`v:20.3`).

It covers artifacts, runs, metadata, deployment health, and datasets together, giving auditors a route from a score to the model and feature inputs. The MLOps Principles and Continuous Intelligence sources support this broader traceability.

### Consequences

* Record model and feature references per score.
* Maintain versioned training and deployment metadata.

## Pros and Cons of the Options

### Comprehensive ML lifecycle traceability

* Good, because Links artifacts and datasets
* Good, because Supports deployment audit
* Bad, because Requires metadata discipline
* Sources: `s08_p01`, `s22_p03`

### Pipeline and experiment version control

* Good, because Reproduces training runs
* Good, because Compares experiments
* Bad, because Less production context
