# What should production monitoring cover?

* System: Card-fraud scoring service

## Context and Problem Statement

Peak availability depends on detecting service and data problems; changing fraud patterns can also reduce model quality. The design space treats monitoring practices as combinable.

## Decision Drivers

* Availability: service health
* Auditability: score traceability

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

Peak availability decides the choice: observing latency, uptime, and data quality makes service and input problems visible. This adds monitoring and response work; the design space does not specify fraud-specific quality thresholds.

### Consequences

* Define alerts and ownership for service and data anomalies.
* Preserve operational logs needed to investigate scoring behavior.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Availability: tracks latency and uptime
* Good, because Auditability: observes data quality and shifts
* Bad, because Cost: monitoring adds operational work
* Bad, because Availability: alerts require response procedures
* Sources: `s04_p02`, `s06_p02`, `s06_p13`, `s21_p10`

### Passive production operation

* Good, because Cost: minimal monitoring overhead
* Bad, because Availability: failures may go unnoticed
* Bad, because Auditability: little evidence about production behavior
