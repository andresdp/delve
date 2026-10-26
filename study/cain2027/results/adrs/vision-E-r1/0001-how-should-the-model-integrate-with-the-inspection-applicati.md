# How should the model integrate with the inspection application?

* System: On-device visual inspection

## Context and Problem Statement

The model runs on production line cameras, where connectivity may be unavailable. The design space offers application integration patterns, but does not specify device packaging.

## Decision Drivers

* intermittent network
* small team
* tight budget

## Considered Options

* Model as module in modular monolith (`v:1.3`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model as module in modular monolith" (`v:1.3`).

A module keeps the model close to the camera application and limits operational overhead. The checked combination had no warnings, but no attesting sources.

### Consequences

* Package and update model with the application.
* Keep model interfaces distinct within the application.

## Pros and Cons of the Options

### Model as module in modular monolith

* Good, because simple deployment
* Good, because clear module boundary
* Bad, because shared application lifecycle
* Sources: `d:1`, `v:1.3`

### Model as a service

* Good, because independent model service
* Bad, because service overhead
* Bad, because network dependency
* Sources: `d:1`, `v:1.1`
