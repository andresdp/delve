# How should production classification quality be monitored?

* System: Large-scale document classification

## Context and Problem Statement

Operators need to see when quality drifts. Monitoring model performance is a modeled option, but the brief does not specify available labels or quality measures.

## Decision Drivers

* detect quality drift
* operator visibility
* unknown label availability

## Considered Options

* Model performance monitoring (`v:22.1`)
* Monitoring or logging data and predictions (`v:22.2`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

The explicit requirement is to see classification quality drift, making performance monitoring the closest modeled option. The checked point had no warnings and no attesting sources.

### Consequences

* Define quality metrics and alert thresholds.
* Arrange timely quality signals, including labels if required.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because tracks performance measures
* Good, because targets quality drift
* Bad, because depends on defined metrics
* Sources: `d:22`, `v:22.1`

### Monitoring or logging data and predictions

* Good, because records inputs and outputs
* Good, because supports operational review
* Bad, because logs alone do not prove quality
* Sources: `d:22`, `v:22.2`

### No in-production monitoring

* Good, because less monitoring overhead
* Bad, because drift may go unseen
* Sources: `d:22`, `v:22.3`
