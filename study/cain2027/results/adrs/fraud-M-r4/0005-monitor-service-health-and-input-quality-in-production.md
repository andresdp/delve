# Monitor service health and input quality in production

* System: Card-fraud scoring service

## Context and Problem Statement

Peak traffic and strict response times make operational failures visible risks; changing transaction data can also degrade scores.

## Decision Drivers

* Latency target
* Peak reliability
* Changing inputs

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Real-time prediction-quality monitoring (`v:6.1`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

This monitoring covers latency, uptime, dependencies, input quality, and data shifts, directly addressing the brief’s operational constraints. Real-time quality checks can complement it when labels become available; monitoring practices are combinable in this dimension (Productionizing Machine Learning with a Microservices Architecture; MLOps Principles).

### Consequences

* Alert on latency, availability, dependency, and input-quality breaches.
* Decide separately how label delays affect model-quality alerts.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Tracks latency and uptime
* Good, because Covers data quality and shifts
* Bad, because Requires monitoring thresholds
* Sources: `s04_p02`, `s06_p02`, `s22_p04`

### Real-time prediction-quality monitoring

* Good, because Tracks model behavior
* Good, because Can expose quality changes
* Bad, because Needs timely labels
* Sources: `s04_p12`, `s06_p06`, `s23_p03`

### Passive production operation

* Good, because Minimal monitoring setup
* Bad, because No active issue tracking
* Sources: `s13_p10`, `s23_p13`
