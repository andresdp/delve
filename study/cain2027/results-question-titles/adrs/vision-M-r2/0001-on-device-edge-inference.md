# On-device edge inference

*Where should inference run?*

* System: On-device visual inspection

## Context and Problem Statement

Cameras operate on production lines that often lack network access, so inspection must remain available locally.

## Decision Drivers

* Intermittent network
* Production-line inspection

## Considered Options

* On-device edge inference (`v:30.4`)
* Model-as-a-service deployment (`v:30.3`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

The brief requires inspection on cameras that may have no network access. Sources including “Composing Deep-Learning Microservices for the Hybrid Internet of Things” and “Three Levels of ML Software” document on-device inference (s07_p01, s19_p11).

### Consequences

* Package inference for the target device.
* Plan for device-side model updates.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Runs on device
* Good, because Works offline
* Bad, because Device deployment required
* Sources: `s01_p06`, `s07_p01`, `s19_p11`

### Model-as-a-service deployment

* Good, because Centralized serving
* Good, because Integrates with applications
* Bad, because Needs network connectivity
* Sources: `s01_p08`, `s04_p01`, `s06_p13`
