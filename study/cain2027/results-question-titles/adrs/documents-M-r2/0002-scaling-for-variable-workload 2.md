# Scaling for variable workload

* System: Large-scale document classification

## Context and Problem Statement

Document volume changes considerably over the year, so capacity needs to follow workload. The brief does not specify latency or cost targets.

## Decision Drivers

* Seasonal volume
* Large workload
* Capacity flexibility

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Elastic scaling addresses the explicit seasonal workload swings; the rival scale-to-zero choice may be less suitable when high-volume scoring needs ready capacity. “Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2” discusses elastic resources. The checked combination was unattested.

### Consequences

* Capacity changes with scoring demand.
* Peak throughput still needs sizing and observation.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Capacity follows demand
* Good, because Supports large workloads
* Bad, because Requires scaling controls
* Sources: `s02_p01`

### Scale-to-zero serving

* Good, because Reduces idle capacity
* Good, because Controls serving cost
* Bad, because May add startup delay
* Sources: `s11_p04`
