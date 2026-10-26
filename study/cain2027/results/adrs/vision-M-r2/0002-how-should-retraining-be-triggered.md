# How should retraining be triggered?

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images arrive for a recurring weekly retraining cycle. The small team benefits from a repeatable trigger with limited manual operation.

## Decision Drivers

* Weekly retraining
* Small team
* New labelled images

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

A weekly schedule directly fits the stated retraining cadence and reduces repeated operator work. “MLOps: Continuous delivery and automation pipelines in machine learning” describes recurring scheduled triggers (s06_p07).

### Consequences

* Automate a weekly training start.
* Define behavior when the latest labels are unavailable.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Matches weekly cadence
* Good, because Predictable operation
* Bad, because May run without new labels
* Sources: `s02_p08`, `s06_p07`, `s20_p06`

### Manual retraining trigger

* Good, because Human-controlled timing
* Bad, because Recurring manual effort
* Sources: `s06_p11`, `s19_p08`
