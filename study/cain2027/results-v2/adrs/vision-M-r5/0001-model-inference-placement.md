# Model inference placement

* System: On-device visual inspection

## Context and Problem Statement

Cameras must detect defects when network access is unavailable. The brief specifies on-device execution but no prediction latency target.

## Decision Drivers

* Offline inference
* Small-team operations

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Offline inference decides the choice: on-device execution works without a network, at the cost of managing device deployments. This is supported by “Composing Deep-Learning Microservices for the Hybrid Internet of Things” and “Three Levels of ML Software.”

### Consequences

* Each device needs a deployable model runtime.
* Devices must receive model updates when connected.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Offline inference: runs on device
* Bad, because Small-team operations: device rollout to manage
* Sources: `s07_p01`, `s19_p11`

### Model-as-a-service deployment

* Good, because Small-team operations: centralized serving
* Bad, because Offline inference: depends on network
* Sources: `s19_p08`, `s25_p06`
