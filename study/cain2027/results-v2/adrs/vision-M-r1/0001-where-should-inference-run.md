# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras operate along production lines, often without network access, so predictions must be available locally. The design space describes both on-device inference and offline containerized services.

## Decision Drivers

* Offline operation
* Local inference

## Considered Options

* On-device edge inference (`v:30.4`)
* Containerized offline prediction service (`v:30.1`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Offline operation decides the choice: the model runs on the cameras even without network access, at the cost of managing model deployment across devices. This aligns with “Composing Deep-Learning Microservices for the Hybrid Internet of Things” and “Three Levels of ML Software.”

### Consequences

* Package and distribute compatible model artifacts to cameras.
* Device updates and recovery need to work when connectivity returns.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Offline operation: inference runs on the device
* Bad, because Tight budget: device rollout and support
* Sources: `s07_p01`, `s19_p11`

### Containerized offline prediction service

* Good, because Offline operation: supports local batch prediction
* Bad, because Local inference: service requires device-side runtime
* Sources: `s02_p11`, `s22_p13`
