# Elastic resource scaling

*How should compute scale with demand?*

* System: Large-scale document classification

## Context and Problem Statement

Classification volume reaches millions per day and varies strongly by season, so capacity must handle peaks without remaining fixed year round.

## Decision Drivers

* Millions of documents daily
* Seasonal volume swings

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Fixed-capacity deployment

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Choose elastic capacity for seasonal demand changes. This is supported by “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” and “Productionizing Machine Learning with a Microservices Architecture.”

### Consequences

* Capacity must scale and contract with workload.
* Scaling behavior needs operational monitoring.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adjusts to workload demand
* Good, because Supports peak capacity
* Bad, because Scaling needs operational controls
* Sources: `s02_p01`, `s04_p06`, `s15_p04`

### Fixed-capacity deployment

* Good, because Predictable capacity
* Good, because Simple sizing
* Bad, because Can waste off-season capacity
* Bad, because May constrain peak throughput
