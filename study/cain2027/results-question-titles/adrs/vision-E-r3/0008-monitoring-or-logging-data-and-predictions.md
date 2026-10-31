# Monitoring or logging data and predictions

*How to monitor models in production?*

* System: On-device visual inspection

## Context and Problem Statement

Devices operate along production lines and may be disconnected from the network. The team needs operational visibility without assuming continuous connectivity.

## Decision Drivers

* Intermittent connectivity
* Defect inspection
* Small team

## Considered Options

* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Monitoring or logging data and predictions" (`v:22.2`).

Logging data and predictions can support later review when devices reconnect, while performance monitoring needs a practical source of quality signals. The design point has no warnings, but no attesting sources.

### Consequences

* Buffer useful logs locally during outages.
* Plan how logs are collected and reviewed.

## Pros and Cons of the Options

### Monitoring or logging data and predictions

* Good, because Captures inputs and outputs
* Bad, because Requires storage and review
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Tracks model performance
* Bad, because Needs performance signals
* Sources: `d:22`, `v:22.1`

### No in-production monitoring

* Good, because No monitoring infrastructure
* Bad, because Limited failure visibility
* Sources: `d:22`, `v:22.3`
