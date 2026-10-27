# Publish classification results through a shared service interface

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, so the system needs a common way to make them available.

## Decision Drivers

* Several consuming teams
* Shared classification results

## Considered Options

* Shared service interface
* Separate team integrations

## Decision Outcome

Chosen option: "Shared service interface".

A common interface serves multiple teams with consistent access to results.

### Consequences

* Requires interface ownership
* Consumer needs may require versioning

## Pros and Cons of the Options

### Shared service interface

* Good, because One integration point
* Good, because Consistent results
* Bad, because Service availability matters
* Bad, because Interface needs governance

### Separate team integrations

* Good, because Team-specific flexibility
* Good, because Independent integration
* Bad, because Duplicated work
* Bad, because Inconsistent consumption
