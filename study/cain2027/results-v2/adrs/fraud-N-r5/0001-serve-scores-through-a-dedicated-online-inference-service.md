# Serve scores through a dedicated online inference service

* System: Card-fraud scoring service

## Context and Problem Statement

Every card transaction needs a fraud score before authorization, with results in tens of milliseconds. The service must sustain peaks.

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability
* Auditor traceability

## Considered Options

* Dedicated online inference service
* Run inference inside the authorization service
* Call a hosted third-party scoring API

## Decision Outcome

Chosen option: "Dedicated online inference service".

Tens-of-milliseconds latency decides the choice: a dedicated service can keep models loaded and scale for scoring demand. It costs an additional service dependency.

### Consequences

* Maintain a low-latency network path from authorization to scoring.
* Scale serving capacity independently and monitor its availability.
* Keep authorization behavior defined for scoring timeouts.

## Pros and Cons of the Options

### Dedicated online inference service

* Good, because Tens-of-milliseconds latency: keep models loaded in memory
* Good, because Peak availability: scale serving capacity independently
* Bad, because Peak availability: adds a service dependency

### Run inference inside the authorization service

* Good, because Tens-of-milliseconds latency: avoids a network hop
* Good, because Peak availability: fewer service dependencies
* Bad, because Peak availability: scoring competes with authorization workloads
* Bad, because Auditor traceability: model changes couple to service releases

### Call a hosted third-party scoring API

* Good, because Peak availability: provider manages serving capacity
* Bad, because Tens-of-milliseconds latency: network and provider latency
* Bad, because Auditor traceability: less control over scoring records
