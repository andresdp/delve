# Store training images in a shared data store

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining needs access to newly labelled images. A shared store provides a straightforward source for the training pipeline.

## Decision Drivers

* Weekly retraining
* Small team
* Budget constraints

## Considered Options

* Shared data store (`v:2.1`)
* Data service (`v:2.2`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

A shared store gives the weekly training workflow a common image source with modest operational overhead (d:2, v:2.1).

### Consequences

* Training infrastructure needs store access.
* Retention and capacity policies remain to be set.

## Pros and Cons of the Options

### Shared data store

* Good, because Central training source
* Good, because Simple access
* Bad, because Storage needs management
* Sources: `d:2`, `v:2.1`

### Data service

* Good, because Encapsulated access
* Bad, because Service to operate
* Sources: `d:2`, `v:2.2`
