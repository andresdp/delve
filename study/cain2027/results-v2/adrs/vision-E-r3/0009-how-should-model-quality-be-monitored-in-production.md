# How should model quality be monitored in production?

* System: On-device visual inspection

## Context and Problem Statement

Models run on devices that may be offline, limiting centralized observation. Some monitoring is needed to detect degradation, but the brief gives no telemetry budget or connectivity assumptions.

## Decision Drivers

* Reliable inspection
* Offline operation
* Tight infrastructure budget

## Considered Options

* Model performance monitoring (`v:22.1`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Reliable inspection decides for monitoring, giving up some budget to detect quality degradation; collection and transfer during offline periods remain unresolved.

### Consequences

* Monitoring needs a way to measure model quality.
* Offline periods require deferred reporting or local review.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Reliable inspection: tracks model quality
* Bad, because Offline operation: metrics may not reach a central monitor
* Sources: `d:22`, `v:22.1`

### No in-production monitoring

* Good, because Budget: avoids monitoring infrastructure
* Bad, because Reliable inspection: degradation may go undetected
* Sources: `d:22`, `v:22.3`
