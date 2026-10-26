# How should classification results reach consumers?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classification results, so delivery should support independent consumers without coupling them to classifier internals.

## Decision Drivers

* several consumers
* classification results

## Considered Options

* Shared results database
* Versioned events per result

## Decision Outcome

Chosen option: "Versioned events per result".

Versioned result events let teams consume classifications independently and accommodate future schema changes.

### Consequences

* Consumers must handle duplicate delivery.
* Event schema changes need version management.

## Pros and Cons of the Options

### Shared results database

* Good, because easy querying
* Good, because central record
* Bad, because consumer coupling
* Bad, because shared load

### Versioned events per result

* Good, because consumer independence
* Good, because replay support
* Bad, because delivery coordination
* Bad, because duplicate handling
