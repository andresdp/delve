# Store shared training data in a shared data store

* System: On-device visual inspection

## Context and Problem Statement

The system needs a place for labelled images used by recurring training. Data storage should support the training workflow without prescribing a specific product.

## Decision Drivers

* Training data retention
* Weekly retraining
* Tight budget

## Considered Options

* Shared data store (`v:2.1`)
* Data service (`v:2.2`)
* No data store (`v:2.4`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

A shared store provides a simple place for the training workflow to access retained images (d:2, v:2.1).

### Consequences

* Storage capacity and retention need management.
* The brief does not determine storage technology or location.

## Pros and Cons of the Options

### Shared data store

* Good, because Shared data access
* Good, because Straightforward storage
* Bad, because Store must be operated
* Sources: `d:2`, `v:2.1`

### Data service

* Good, because Access through services
* Bad, because Service to maintain
* Sources: `d:2`, `v:2.2`

### No data store

* Good, because Avoids storage layer
* Bad, because Poor fit for recurring image training
* Sources: `d:2`, `v:2.4`
