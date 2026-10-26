# How should training and labelled images be stored?

* System: On-device visual inspection

## Context and Problem Statement

Retraining uses newly labelled images, so training needs a durable place to access them. The brief does not specify a shared or networked store, and devices may be offline.

## Decision Drivers

* Weekly retraining
* Offline operation
* Tight infrastructure budget

## Considered Options

* Shared data store (`v:2.1`)
* No data store (`v:2.4`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

Weekly retraining decides for a shared training store, accepting infrastructure cost to centralize labelled images; the design space does not establish a storage topology suited to offline devices.

### Consequences

* Training infrastructure needs access to the shared store.
* Device-side inspection must not depend on that store.

## Pros and Cons of the Options

### Shared data store

* Good, because Weekly retraining: provides a common training dataset
* Bad, because Offline operation: store access may be unavailable at devices
* Sources: `d:2`, `v:2.1`

### No data store

* Good, because Budget: avoids shared storage infrastructure
* Bad, because Weekly retraining: organizing inputs becomes manual
* Sources: `d:2`, `v:2.4`
