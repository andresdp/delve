# Shared data store

*Where should documents and results be stored?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classifications, so prediction results need a shared access point. The brief does not specify a storage technology or retention policy.

## Decision Drivers

* Multiple consumers
* High volume
* Classification results

## Considered Options

* Shared data store (`v:2.1`)
* Data service (`v:2.2`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

A shared store offers a straightforward way for multiple teams to consume completed batch results. The checked batch combination has no warnings, but is unattested (`attested_by` is empty).

### Consequences

* Teams need agreed result schemas and access controls.
* Storage capacity and retention must be sized separately.

## Pros and Cons of the Options

### Shared data store

* Good, because Common access point
* Good, because Supports batch result reads
* Bad, because Access and retention need governance
* Sources: `d:2`, `v:2.1`

### Data service

* Good, because Encapsulates data access
* Good, because Can centralize policy
* Bad, because Adds service dependency
* Sources: `d:2`, `v:2.2`
