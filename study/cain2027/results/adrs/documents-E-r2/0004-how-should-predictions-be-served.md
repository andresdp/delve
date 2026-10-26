# How should predictions be served?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, and the brief does not state that they need synchronous responses.

## Decision Drivers

* multiple consumers
* high volume

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)
* Hybrid online/offline model serving (`v:5.5`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Scheduled batch serving produces stored results that multiple teams can consume without imposing a real-time service requirement. The checked point had no warnings but no source-attested systems.

### Consequences

* Teams need access to the result store.
* Results are available after the serving run.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because writes results to shared storage
* Good, because suits scheduled high volume
* Bad, because not immediate
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because real-time delivery
* Good, because distributed service
* Bad, because serving capacity management
* Sources: `d:5`, `v:5.1`

### Hybrid online/offline model serving

* Good, because supports both response modes
* Bad, because two serving paths
* Sources: `d:5`, `v:5.5`
