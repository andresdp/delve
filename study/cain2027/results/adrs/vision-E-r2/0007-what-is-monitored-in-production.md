# What is monitored in production?

* System: On-device visual inspection

## Context and Problem Statement

Devices may be disconnected, limiting immediate central visibility into predictions. The design space includes prediction logging and model performance monitoring (d:22).

## Decision Drivers

* Offline devices
* Defect detection quality
* Tight infrastructure budget

## Considered Options

* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)

## Decision Outcome

Chosen option: "Monitoring or logging data and predictions" (`v:22.2`).

Logging inputs and predictions gives disconnected devices a basis for later review and delayed quality assessment (d:22, v:22.2).

### Consequences

* Bound local log retention and storage use.
* Provide a sync path for devices when connectivity returns.

## Pros and Cons of the Options

### Monitoring or logging data and predictions

* Good, because Captures operational evidence
* Good, because Can sync when connected
* Bad, because Requires local storage
* Bad, because Labels may arrive later
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Tracks model quality
* Good, because Can reveal regressions
* Bad, because Needs trustworthy labels
* Bad, because Feedback may be delayed
* Sources: `d:22`, `v:22.1`
