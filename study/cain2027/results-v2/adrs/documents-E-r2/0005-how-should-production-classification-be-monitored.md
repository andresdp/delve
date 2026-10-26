# How should production classification be monitored?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts. The design space distinguishes monitoring system data and predictions from monitoring model performance (d:22).

## Decision Drivers

* Drift visibility

## Considered Options

* Monitoring or logging data and predictions (`v:22.2`)
* Model performance monitoring (`v:22.1`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Drift visibility decides the choice because the requirement is explicitly about classification quality. This gives up the broader operational trace that logging inputs and predictions can provide.

### Consequences

* Quality measures must be selected.
* Monitoring requires a way to assess model performance.

## Pros and Cons of the Options

### Monitoring or logging data and predictions

* Good, because Drift visibility: retain inputs and predictions for inspection
* Bad, because Drift visibility: logs alone do not establish model quality
* Sources: `d:22`, `v:22.2`

### Model performance monitoring

* Good, because Drift visibility: observe model performance parameters
* Bad, because Drift visibility: requires suitable quality measures
* Sources: `d:22`, `v:22.1`
