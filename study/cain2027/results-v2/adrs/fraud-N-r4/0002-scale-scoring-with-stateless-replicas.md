# Scale scoring with stateless replicas

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during peaks while returning scores quickly. Replicas can serve requests independently if model artifacts are available to each one.

## Decision Drivers

* Continuous peak operation
* Tens-of-milliseconds latency

## Considered Options

* Stateless scoring replicas
* Single centralized scoring service

## Decision Outcome

Chosen option: "Stateless scoring replicas".

Peak operation decides this choice: independent replicas can add serving capacity as load rises. It costs additional work to distribute and keep model artifacts consistent.

### Consequences

* Deployments need to manage replica capacity and artifact consistency.

## Pros and Cons of the Options

### Stateless scoring replicas

* Good, because Peak operation: add replicas to serve more requests
* Good, because Latency: score without a central inference hop
* Bad, because Peak operation: model artifacts must be distributed to replicas

### Single centralized scoring service

* Good, because Latency: one serving endpoint to manage
* Bad, because Peak operation: centralized capacity can become a bottleneck
