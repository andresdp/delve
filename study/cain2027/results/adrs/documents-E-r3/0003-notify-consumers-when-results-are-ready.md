# Notify consumers when results are ready

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume predictions produced by a high-volume classifier. The design space considers notification, polling, and blocking for result availability (d:6).

## Decision Drivers

* Multiple consuming teams
* Batch completion

## Considered Options

* Push notification (`v:6.1`)
* Polling (`v:6.2`)

## Decision Outcome

Chosen option: "Push notification" (`v:6.1`).

A notification can tell multiple teams when a batch is ready without requiring them to repeatedly check. The serving decision affects how consumers learn results are available (d:5, d:6).

### Consequences

* Consumers need a way to receive notifications.
* Specify retry and missed-notification handling.

## Pros and Cons of the Options

### Push notification

* Good, because Signals result availability
* Good, because Avoids repeated checks
* Bad, because Requires notification handling
* Sources: `d:6`, `v:6.1`

### Polling

* Good, because Simple consumer model
* Good, because Consumers control check timing
* Bad, because Repeated checks add load
* Sources: `d:6`, `v:6.2`
