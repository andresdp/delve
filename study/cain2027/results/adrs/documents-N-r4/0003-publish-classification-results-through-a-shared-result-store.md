# Publish classification results through a shared result store and interface

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classifier's results. A common publication path gives consumers a consistent way to retrieve them.

## Decision Drivers

* Several consumer teams
* Shared results

## Considered Options

* Shared result store and interface
* Direct delivery to each team

## Decision Outcome

Chosen option: "Shared result store and interface".

A shared interface serves multiple teams without requiring the classifier to maintain a separate integration for each.

### Consequences

* The interface needs a stable result schema.
* Consumer access patterns need coordination.

## Pros and Cons of the Options

### Shared result store and interface

* Good, because Consistent access
* Good, because Decouples consumers
* Bad, because Requires interface ownership

### Direct delivery to each team

* Good, because Consumer-specific delivery
* Bad, because Duplicate integrations
* Bad, because Tighter coupling
