# How should model changes be deployed and attributed?

* System: Large-scale document classification

## Context and Problem Statement

The system needs to distinguish changes in classification behavior from changes in incoming documents. Recording the model version with each result supports comparisons when quality drift appears.

## Decision Drivers

* Quality drift: operator visibility
* High volume: millions per day

## Considered Options

* Deploy the latest model without per-result versioning
* Version models and record version per result

## Decision Outcome

Chosen option: "Version models and record version per result".

Quality drift visibility decides the choice: per-result versioning supports attribution across model changes. It costs extra metadata storage and model lifecycle management.

### Consequences

* Include model version in stored results.
* Track deployments alongside quality signals.
* Manage version lifecycle and rollback procedures.

## Pros and Cons of the Options

### Deploy the latest model without per-result versioning

* Good, because High volume: minimal result metadata
* Bad, because Quality drift: harder to attribute behavior changes

### Version models and record version per result

* Good, because Quality drift: compare results by model version
* Bad, because High volume: store and manage version metadata
