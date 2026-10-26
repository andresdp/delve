# Production service and data monitoring

* System: Card-fraud scoring service

## Context and Problem Statement

The service must continue operating during peaks, and its scores and inputs may need investigation later. Monitoring only model quality would miss latency, uptime, and data-quality failures.

## Decision Drivers

* Peak availability
* Audit traceability

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Software-metrics-only monitoring (`v:6.10`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

Peak availability decides the choice: service health and dependency signals expose production failures, while data-quality monitoring helps investigate scoring inputs. The trade-off is added monitoring effort, and score-level audit records still need explicit lineage capture.

### Consequences

* Alert on latency, uptime, dependencies, and data-quality failures.
* Link monitoring events to score and lineage records where possible.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Peak availability: tracks latency, uptime, and dependencies
* Good, because Audit traceability: observes data quality and shifts
* Bad, because Peak availability: monitoring adds operational overhead
* Bad, because Audit traceability: metrics alone do not preserve score-level evidence
* Sources: `s04_p02`, `s06_p02`, `s22_p11`

### Software-metrics-only monitoring

* Good, because Peak availability: surfaces generic service issues
* Good, because Cost: avoids ML-specific monitoring setup
* Bad, because Audit traceability: misses feature and data changes
* Bad, because Peak availability: cannot explain model behavior
