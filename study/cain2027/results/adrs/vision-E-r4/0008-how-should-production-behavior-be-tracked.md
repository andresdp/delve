# How should production behavior be tracked?

* System: On-device visual inspection

## Context and Problem Statement

Devices often lack network access, so operational data and predictions need to be captured locally and collected when connectivity returns.

## Decision Drivers

* Intermittent network
* Production visibility
* Offline devices

## Considered Options

* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)

## Decision Outcome

Chosen option: "Monitoring or logging data and predictions" (`v:22.2`).

Local logging records inputs and predictions during disconnection, allowing review after data can be collected (d:22, v:22.2).

### Consequences

* Logs require local retention limits.
* Results may arrive centrally with delay.

## Pros and Cons of the Options

### Monitoring or logging data and predictions

* Good, because Captures local behavior
* Good, because Supports later review
* Bad, because Uses device storage
* Bad, because Collection may be delayed
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Tracks model metrics
* Bad, because Needs outcome labels
* Bad, because May depend on connectivity
* Sources: `d:22`, `v:22.1`
