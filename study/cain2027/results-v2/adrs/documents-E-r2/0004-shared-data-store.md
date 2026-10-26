# Shared data store

*How should classification data and results be shared?*

* System: Large-scale document classification

## Context and Problem Statement

Multiple teams need classification results, and operators need evidence to assess quality drift. A shared store is one option in the design space (d:2).

## Decision Drivers

* Team consumption
* Drift visibility

## Considered Options

* Shared data store (`v:2.1`)
* Data service (`v:2.2`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

Team consumption decides the choice: a common store gives several teams access to batch results. This gives up service-mediated access controls and requires teams to coordinate access.

### Consequences

* Teams depend on shared storage availability.
* Access permissions need definition.

## Pros and Cons of the Options

### Shared data store

* Good, because Team consumption: common access point for results
* Bad, because Team consumption: access boundaries need coordination
* Sources: `d:2`, `v:2.1`

### Data service

* Good, because Team consumption: access can be mediated through services
* Bad, because Seasonal peak scale: shared service capacity must handle demand
* Sources: `d:2`, `v:2.2`
