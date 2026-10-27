# Run inference on each production line device

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect production lines that often lack network access, so predictions must be available locally.

## Decision Drivers

* Intermittent connectivity
* On-device inference

## Considered Options

* On-device edge inference (`v:30.4`)
* Containerized inference deployment (`v:30.19`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Local inference addresses production lines without reliable network access. “Composing Deep-Learning Microservices for the Hybrid Internet of Things” and “Three Levels of ML Software” describe edge inference.

### Consequences

* Devices need compatible runtimes and local model storage.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Works without network
* Good, because Local predictions
* Bad, because Device resource limits
* Sources: `s07_p01`, `s19_p11`

### Containerized inference deployment

* Good, because Packages dependencies
* Good, because Portable deployment
* Bad, because Does not ensure offline operation
* Sources: `s04_p02`, `s07_p03`
