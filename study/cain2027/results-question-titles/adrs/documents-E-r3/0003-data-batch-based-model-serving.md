# Data batch based model serving

*How to serve classification results*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume predictions, and the brief does not require synchronous responses. A shared result store can support scheduled batch delivery.

## Decision Drivers

* Multiple consumers
* High volume

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)
* Hybrid online/offline model serving (`v:5.5`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Scheduled batch predictions stored for access fit the stated consumers and volume without introducing an unstated real-time requirement (d:5, v:5.3). The batch design point had no warnings; it was unattested, as was the real-time rival.

### Consequences

* Consumers read results from shared storage.
* Define result ownership and freshness expectations.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Writes results to storage
* Good, because Supports batch delivery
* Bad, because Not real time
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Real-time access
* Bad, because Distributed service operations
* Sources: `d:5`, `v:5.1`

### Hybrid online/offline model serving

* Good, because Supports both access patterns
* Bad, because More components
* Sources: `d:5`, `v:5.5`
