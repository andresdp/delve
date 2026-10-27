# Production monitoring

* System: Card-fraud scoring service

## Context and Problem Statement

Peak service operation depends on visibility into availability and latency, while changing inputs can affect score quality. The design space treats monitoring practices as combinable rather than exclusive.

## Decision Drivers

* Peak availability
* Latency visibility
* Data quality

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

Monitoring latency, uptime, and data quality directly supports peak operation and exposes issues that can affect scoring. “Productionizing Machine Learning with a Microservices Architecture” and “MLOps Principles” describe this coverage; passive operation does not meet the service-health need.

### Consequences

* Define operational alerts for latency and availability.
* Track data-quality changes alongside service health.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Covers latency and uptime
* Good, because Tracks data quality and shifts
* Bad, because Needs alert thresholds and ownership
* Bad, because Does not itself prescribe retraining
* Sources: `s04_p02`, `s06_p02`, `s06_p13`, `s21_p10`, `s22_p04`, `s22_p11`, `s23_p04`

### Passive production operation

* Good, because Less monitoring infrastructure
* Good, because Fewer operational alerts
* Bad, because No active performance visibility
* Bad, because Failures may go undetected
