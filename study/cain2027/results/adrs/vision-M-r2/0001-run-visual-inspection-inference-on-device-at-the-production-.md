# Run visual inspection inference on-device at the production line

* System: On-device visual inspection

## Context and Problem Statement

Cameras operate along production lines that often lack network access, so predictions need to be available locally. The design space also includes server-hosted prediction services as an alternative.

## Decision Drivers

* Intermittent network
* Production-line inference

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

The brief requires inspection where network access is often unavailable. “Composing Deep-Learning Microservices for the Hybrid Internet of Things” and “Three Levels of ML Software” document on-device inference; the checked rival point used a networked model service.

### Consequences

* Package and deploy model updates to devices.
* Device compatibility and rollout details need further design.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Local predictions
* Good, because Works offline
* Bad, because Device deployment effort
* Sources: `s01_p06`, `s07_p01`, `s19_p11`, `s24_p01`, `s25_p07`

### Model-as-a-service deployment

* Good, because Centralized serving
* Good, because Shared operations
* Bad, because Needs network access
* Sources: `s01_p08`, `s04_p01`, `s06_p13`, `s09_p01`, `s13_p11`, `s16_p04`, `s19_p08`, `s19_p13`, `s19_p14`, `s20_p09`, `s21_p18`, `s23_p07`, `s25_p06`, `s25_p09`
