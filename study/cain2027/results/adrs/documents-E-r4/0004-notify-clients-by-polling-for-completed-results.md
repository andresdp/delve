# Notify clients by polling for completed results

* System: Large-scale document classification

## Context and Problem Statement

Batch serving writes predictions to storage, while the brief does not specify how clients learn that a batch is complete. Polling is one supported availability pattern (d:6).

## Decision Drivers

* Several consuming teams
* Batch result availability
* No notification requirement specified

## Considered Options

* Polling (`v:6.2`)
* Push notification (`v:6.1`)

## Decision Outcome

Chosen option: "Polling" (`v:6.2`).

Polling fits results written after batch processing and avoids assuming a notification service not called for in the brief. The design space says serving choices affect client availability choices (d:5 to d:6).

### Consequences

* Clients need a result status endpoint or equivalent.
* Polling frequency affects load and freshness.

## Pros and Cons of the Options

### Polling

* Good, because Simple client interaction
* Good, because Clients control retrieval
* Bad, because Repeated status requests
* Sources: `d:6`, `v:6.2`

### Push notification

* Good, because Notifies clients on availability
* Good, because Avoids repeated checks
* Bad, because Requires notification delivery
* Sources: `d:6`, `v:6.1`
