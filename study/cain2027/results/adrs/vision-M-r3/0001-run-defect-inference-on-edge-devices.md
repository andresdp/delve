# Run defect inference on edge devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect defects on production lines where network access is often unavailable. Inference therefore needs to run at the line, near the cameras.

## Decision Drivers

* Often offline
* Production-line cameras

## Considered Options

* On-device edge inference (`v:30.4`)
* Containerized offline prediction service (`v:30.1`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

The brief places cameras along production lines and says network access is often unavailable, favoring local device inference. Sources including “Composing Deep-Learning Microservices for the Hybrid Internet of Things” describe this placement (s07_p01).

### Consequences

* Each device needs a compatible model runtime.
* Inference can continue during network outages.
* Device fleet rollout details remain undecided.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Inference on device
* Good, because Works without network
* Bad, because Device deployment effort
* Bad, because Hardware limits apply
* Sources: `s01_p06`, `s07_p01`, `s19_p11`, `s24_p01`, `s25_p07`

### Containerized offline prediction service

* Good, because Packaged dependencies
* Good, because Supports offline prediction
* Bad, because Requires container runtime
* Bad, because May not fit device
* Sources: `s02_p11`, `s11_p04`, `s19_p15`, `s22_p13`, `s25_p04`
