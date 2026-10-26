# Elastic resource scaling

*How should serving capacity respond to transaction peaks?*

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during peaks and answer within tens of milliseconds. Capacity must be available as demand changes.

## Decision Drivers

* Peak availability
* Low latency
* Variable demand

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic capacity addresses peaks while keeping the online service available. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” discuss scaling resources with workload demand.

### Consequences

* Provision headroom for sudden demand increases.
* Validate scaling against the response-time target.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adjusts capacity to demand
* Good, because Supports peak workloads
* Bad, because Scaling behavior needs tuning
* Sources: `s02_p01`, `s04_p02`, `s15_p04`

### Scale-to-zero serving

* Good, because Reduces idle capacity
* Bad, because Cold starts risk latency
* Sources: `s21_p15`
