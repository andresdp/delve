# Staged update service

*How should weekly models reach devices?*

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and pushed to devices that may often lack network access. Distribution must handle both regular updates and periods without connectivity.

## Decision Drivers

* Weekly retraining
* Intermittent connectivity
* Small team

## Considered Options

* Direct device downloads
* Staged update service
* Removable-media updates

## Decision Outcome

Chosen option: "Staged update service".

A staged service provides a way to push weekly models and coordinate device rollout, while offline devices can receive updates when they reconnect. It adds infrastructure, so the service should remain small in scope given the team and budget constraints.

### Consequences

* Devices without connectivity remain on an older model until updated.
* The team must operate update distribution and track versions.

## Pros and Cons of the Options

### Direct device downloads

* Good, because Few distribution components
* Good, because Devices fetch updates
* Bad, because Needs device connectivity
* Bad, because Fleet coordination burden

### Staged update service

* Good, because Central rollout control
* Good, because Can track deployment
* Bad, because More infrastructure
* Bad, because Offline devices lag

### Removable-media updates

* Good, because Works offline
* Good, because Low service cost
* Bad, because Manual handling
* Bad, because Slower fleet rollout
