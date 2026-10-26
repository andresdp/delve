# How should weekly retraining start?

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for retraining every week. The design space describes both scheduled retraining and retraining after drift or performance changes.

## Decision Drivers

* Weekly update cadence
* Small team

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Performance- or drift-based retraining trigger (`v:6.8`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

The weekly update cadence decides the choice: a scheduled trigger directly fits the stated process. This gives up triggering additional retraining between scheduled runs when drift or quality changes.

### Consequences

* Automate a weekly training run.
* Validate newly labelled data before using it.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Weekly cadence: directly matches the brief
* Good, because Small team: predictable automation
* Bad, because Small team: requires schedule operations
* Sources: `s02_p08`, `s06_p07`, `s06_p11`, `s20_p06`, `s22_p08`

### Performance- or drift-based retraining trigger

* Good, because Small team: can avoid unnecessary retraining
* Good, because Model quality: responds to detected change
* Bad, because Weekly cadence: does not ensure weekly updates
* Bad, because Small team: needs drift or quality monitoring
