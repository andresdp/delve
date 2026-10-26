# How should shared results be stored?

* System: Large-scale document classification

## Context and Problem Statement

Several teams need to consume the same classification results, so the architecture needs a shared handoff point.

## Decision Drivers

* multiple consumers
* batch results

## Considered Options

* Shared data store (`v:2.1`)
* Event store (`v:2.3`)
* Data service (`v:2.2`)

## Decision Outcome

Chosen option: "Shared data store" (`v:2.1`).

A shared store provides a straightforward handoff for batch predictions to several teams. The chosen point had no warnings, but the design space provides no source-attested combinations.

### Consequences

* Consumer access controls are required.
* Store availability affects downstream teams.

## Pros and Cons of the Options

### Shared data store

* Good, because common access point
* Good, because fits batch outputs
* Bad, because access and ownership coordination
* Sources: `d:2`, `v:2.1`

### Event store

* Good, because stores exchanged events
* Good, because supports stream flow
* Bad, because less aligned to batch choice
* Sources: `d:2`, `v:2.3`

### Data service

* Good, because central access interface
* Bad, because service becomes dependency
* Sources: `d:2`, `v:2.2`
