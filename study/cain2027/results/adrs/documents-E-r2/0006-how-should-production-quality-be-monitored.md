# How should production quality be monitored?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when classification quality drifts, so production monitoring must expose model performance over time.

## Decision Drivers

* quality drift visibility
* operator action

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* Model in-production tracking (`v:22.4`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring most directly addresses the stated need to detect classification quality drift. The checked point had no warnings and no source-attested systems.

### Consequences

* Quality indicators and thresholds must be defined.
* Operators need a review path when measures shift.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because tracks performance measures
* Good, because directly signals quality change
* Bad, because depends on quality indicators
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because records inputs and outputs
* Good, because supports later analysis
* Bad, because logs alone do not show quality
* Sources: `d:22`, `v:22.2`

### Model in-production tracking

* Good, because tracks usage and outputs
* Good, because broader operational context
* Bad, because wider tracking scope
* Sources: `d:22`, `v:22.4`
