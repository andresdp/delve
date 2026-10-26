# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras on production lines need defect predictions where network access is often unavailable.

## Decision Drivers

* offline operation
* on-device inference

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

It supports prediction on devices without relying on network access. The checked design point had no warnings, though its combination of values was unattested.

### Consequences

* Ship the model and inference runtime to each device.
* Plan for device fleet updates and rollback.

## Pros and Cons of the Options

### On-device edge inference

* Good, because works offline
* Good, because local predictions
* Bad, because device constraints
* Bad, because fleet deployment effort
* Sources: `s07_p01`, `s19_p11`

### Model-as-a-service deployment

* Good, because centralized serving
* Good, because simpler model updates
* Bad, because needs connectivity
* Bad, because network dependency
