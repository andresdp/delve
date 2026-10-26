# How should the model integrate with the camera application?

* System: On-device visual inspection

## Context and Problem Statement

The model must run alongside the inspection application on devices with intermittent connectivity.

## Decision Drivers

* Offline operation
* Low latency
* Tight budget

## Considered Options

* Model in monolith (`v:1.2`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model in monolith" (`v:1.2`).

Offline operation decides the choice: embedding the model keeps application inference self-contained. This gives up independent model-service releases. The design space has no source passages; this choice is grounded in d:1 and v:1.2.

### Consequences

* The application package includes the model.
* App and model updates are coupled.
* Local deployment stays simple.

## Pros and Cons of the Options

### Model in monolith

* Good, because Offline operation: model ships with application
* Good, because Low latency: avoids remote calls
* Bad, because Maintainability: model and app release together
* Sources: `d:1`, `v:1.2`

### Model as a service

* Good, because Maintainability: separates model service
* Bad, because Offline operation: service must be available locally or remotely
* Bad, because Tight budget: adds service deployment
* Sources: `d:1`, `v:1.1`
