# Scale scoring resources elastically

* System: Card-fraud scoring service

## Context and Problem Statement

Traffic peaks require more capacity, while the service still needs low response times. Elastic resource scaling adjusts compute to workload demand.

## Decision Drivers

* Traffic peaks
* Latency target
* Capacity

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling aligns capacity with demand while preserving the service’s ability to handle peaks. Scale-to-zero is a poor fit for a latency-sensitive authorization path because startup delay can affect responses.

### Consequences

* Set a warm minimum serving capacity.
* Measure latency and capacity under peak load.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Adapts capacity to demand
* Good, because Supports peak workloads
* Bad, because Scaling behavior needs tuning
* Sources: `s04_p02`, `s13_p09`

### Scale-to-zero serving

* Good, because Reduces idle resource use
* Good, because Can lower cost
* Bad, because Cold starts threaten latency
