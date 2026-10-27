# Run defect inference on-device

* System: On-device visual inspection

## Context and Problem Statement

Cameras operate along production lines that often lack network access, so prediction must remain available locally.

## Decision Drivers

* Intermittent network
* Line-side inference

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

The design space describes edge inference as running models on deployed devices; that directly fits cameras which often have no network connection. The service alternative depends on network access for predictions.

### Consequences

* Package inference runtime with the device release.
* Plan for local model storage and execution.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Works offline
* Good, because Local predictions
* Bad, because Device deployment effort
* Sources: `s07_p01`, `s19_p11`

### Model-as-a-service deployment

* Good, because Centralized serving
* Good, because Simpler device footprint
* Bad, because Network dependency
* Bad, because Remote availability
* Sources: `s06_p13`, `s25_p06`
