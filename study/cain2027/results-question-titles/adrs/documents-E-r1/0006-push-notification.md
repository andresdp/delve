# Push notification

*How should consumers learn that results are ready?*

* System: Large-scale document classification

## Context and Problem Statement

Batch processing means consumers may need to know when results become available. The brief identifies multiple consumers but does not specify their integration patterns.

## Decision Drivers

* Multiple consumers
* Asynchronous results
* Batch processing

## Considered Options

* Push notification (`v:6.1`)
* Polling (`v:6.2`)

## Decision Outcome

Chosen option: "Push notification" (`v:6.1`).

Push notifications let the system signal completion to multiple consumers without requiring repeated checks. The checked point is novel (`attested_by` is empty), so consumer support for notifications should be confirmed during integration.

### Consequences

* Consumers must provide notification endpoints or subscriptions.
* Delivery failures need retry handling.

## Pros and Cons of the Options

### Push notification

* Good, because Signals readiness promptly
* Good, because Avoids repeated checks
* Bad, because Requires notification handling
* Sources: `d:6`, `v:6.1`

### Polling

* Good, because Simple consumer model
* Good, because Consumers control check timing
* Bad, because Repeated checks add load
* Sources: `d:6`, `v:6.2`
