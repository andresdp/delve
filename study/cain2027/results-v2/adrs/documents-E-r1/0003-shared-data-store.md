# Shared data store

*How should teams access stored results?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the results, so the architecture needs a shared access point. The design space distinguishes shared storage from data services (d:2).

## Decision Drivers

* Several consuming teams
* Millions of documents/day

## Considered Options

* Shared data store (`v:2.1`)
* Data service (`v:2.2`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

Multiple consuming teams decide the choice: a shared store makes batch outputs available in one place, at the cost of planning for concurrent reads.

### Consequences

* Define stable result schemas for consumers.
* Manage access and capacity for concurrent reads.

## Pros and Cons of the Options

### Shared data store

* Good, because Consumers: make results available in one place
* Bad, because Scale: concurrent access needs capacity planning
* Sources: `d:2`, `v:2.1`

### Data service

* Good, because Consumers: provide a managed access interface
* Bad, because Scale: service adds a runtime component
* Sources: `d:2`, `v:2.2`
