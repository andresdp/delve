# Where should inspection inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras operate along production lines that often lack network access. Inference must remain available at the line.

## Decision Drivers

* Offline operation
* Production-line inspection

## Considered Options

* On-device edge inference (`v:30.4`)
* Containerized offline prediction service (`v:30.1`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Choose local inference to keep inspection available offline. “Composing Deep-Learning Microservices for the Hybrid Internet of Things” and “Three Levels of ML Software” document edge inference; this combination had no attesting sources in the checked design point.

### Consequences

* Provision and update models across devices.
* Device compute and storage bound the runtime.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Works without network
* Good, because Inference stays at device
* Bad, because Device runtime constraints
* Bad, because Fleet deployment overhead
* Sources: `s07_p01`, `s19_p11`

### Containerized offline prediction service

* Good, because Packaged runtime
* Good, because Supports scheduled prediction
* Bad, because Needs a service host
* Bad, because Less direct fit for cameras
* Sources: `s02_p09`
