# Serve explicitly versioned models

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must be able to identify which model produced each transaction score.

## Decision Drivers

* Model attribution
* Auditability

## Considered Options

* Versioned model artifacts
* Unversioned mutable model

## Decision Outcome

Chosen option: "Versioned model artifacts".

An immutable version identifier makes each scoring decision attributable to a specific model.

### Consequences

* Each score record must include the model version.
* Model versions need retention and lifecycle rules.

## Pros and Cons of the Options

### Versioned model artifacts

* Good, because Stable model identity
* Good, because Supports historical attribution
* Bad, because Requires artifact lifecycle management

### Unversioned mutable model

* Good, because Simple replacement flow
* Bad, because Historical scores become ambiguous
