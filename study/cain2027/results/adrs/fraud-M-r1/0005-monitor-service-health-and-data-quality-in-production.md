# Monitor service health and data quality in production

* System: Card-fraud scoring service

## Context and Problem Statement

The service must remain available during peaks, while changes in inputs can affect fraud scoring. The brief does not prescribe an automatic model update policy.

## Decision Drivers

* Peak availability
* Score reliability
* Operational visibility

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

Monitoring latency, uptime, dependencies, and input quality directly addresses service availability and scoring reliability. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps Principles” cover service and data monitoring.

### Consequences

* Operational thresholds and response procedures must be defined.
* Monitoring alone does not determine retraining or score policy.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Covers latency and uptime
* Good, because Includes data changes
* Bad, because Requires alerting and response ownership
* Sources: `s04_p02`, `s06_p02`, `s22_p04`, `s23_p04`

### Passive production operation

* Good, because Minimal monitoring setup
* Bad, because Problems may remain unseen
* Sources: `s23_p07`
