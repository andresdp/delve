# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras often lack network access, so inspection must continue locally. The model still needs a repeatable deployment path to the production devices.

## Decision Drivers

* Offline operation
* Production-line inference
* Tight budget

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

Local inference directly meets the offline requirement. Sources including “Composing Deep-Learning Microservices for the Hybrid Internet of Things” describe edge inference; the checked combination is novel in the design space, with no warnings or attesting sources.

### Consequences

* Package and deploy models to each device.
* Plan for local storage and device-specific compatibility.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Runs at the camera
* Good, because Works without network
* Bad, because Device deployment effort
* Bad, because Hardware constraints
* Sources: `s07_p01`, `s19_p11`

### Model-as-a-service deployment

* Good, because Centralized serving
* Good, because Simpler model updates
* Bad, because Requires connectivity
* Bad, because Adds service infrastructure
* Sources: `s06_p13`, `s19_p08`
