# Monitor device health and input data quality

* System: On-device visual inspection

## Context and Problem Statement

Network limitations and resource-constrained devices can hide runtime issues; production inputs may also shift over time.

## Decision Drivers

* Intermittent connectivity
* Device health
* Data quality

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Periodic model health checks (`v:6.18`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

Monitor resource use, uptime, and data quality to surface operational and input problems; the design point checks this together with offline evaluation. “MLOps Principles” and “MLOps: Continuous delivery and automation pipelines in machine learning” describe these monitoring concerns.

### Consequences

* Buffer or summarize telemetry locally when devices are offline.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Tracks runtime and inputs
* Good, because Supports diagnosis
* Bad, because Telemetry needs collection
* Sources: `s06_p02`, `s22_p04`

### Periodic model health checks

* Good, because Recurring review
* Good, because Lower monitoring footprint
* Bad, because Problems may surface later
* Sources: `s20_p03`, `s23_p08`
