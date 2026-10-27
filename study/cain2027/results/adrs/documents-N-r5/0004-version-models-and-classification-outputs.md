# Version models and classification outputs

* System: Large-scale document classification

## Context and Problem Statement

Quality can change as the LLM or its configuration changes. Several consuming teams need results whose origin and meaning can be identified.

## Decision Drivers

* Quality drift
* Several consumers

## Considered Options

* Use an unversioned mutable classifier
* Version model configuration and output schema

## Decision Outcome

Chosen option: "Version model configuration and output schema".

Versioning lets operators relate quality changes to classifier changes and gives consumers a way to interpret results consistently.

### Consequences

* Versions must accompany stored results.
* Schema changes need consumer coordination.

## Pros and Cons of the Options

### Use an unversioned mutable classifier

* Good, because Simple deployment
* Bad, because Hard to attribute changes
* Bad, because Results lack provenance

### Version model configuration and output schema

* Good, because Supports comparisons
* Good, because Makes output changes visible
* Bad, because Adds release coordination
* Bad, because Requires version tracking
