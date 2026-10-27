# Version the classifier and record each prediction's version

* System: Large-scale document classification

## Context and Problem Statement

Operators need to identify when classification quality drifts. Linking predictions to the model or prompt version makes quality changes traceable.

## Decision Drivers

* Quality drift
* Operational diagnosis

## Considered Options

* Versioned classifier with prediction metadata
* Unversioned classifier updates

## Decision Outcome

Chosen option: "Versioned classifier with prediction metadata".

Version metadata makes it possible to compare quality across classifier changes and narrow the cause of observed drift.

### Consequences

* Store version metadata with results.
* Maintain evaluations for each release.

## Pros and Cons of the Options

### Versioned classifier with prediction metadata

* Good, because Enables comparisons
* Good, because Supports rollback diagnosis
* Bad, because Requires release discipline

### Unversioned classifier updates

* Good, because Fewer release artifacts
* Bad, because Changes are hard to trace
* Bad, because Comparisons are unreliable
