# Detecting production quality drift

* System: Large-scale document classification

## Context and Problem Statement

Operators need visibility when classification quality drifts. Drift can be observed from input changes and measured from predictions when labeled outcomes become available.

## Decision Drivers

* Drift visibility
* Operator response
* Quality assurance

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Real-time prediction-quality monitoring (`v:6.1`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Choose input-drift monitoring for timely operator visibility, and treat it as a signal to investigate rather than proof of quality decline. “Productionizing Machine Learning with a Microservices Architecture” describes monitoring feature processes and values. The checked point warned that multiple monitoring values are not exclusive, so monitoring practices can be combined where labels permit.

### Consequences

* Operators receive drift signals for investigation.
* Quality assessment depends on labeled outcomes, whose availability is unspecified.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Surfaces input changes
* Good, because Can alert operators early
* Bad, because Input shifts do not prove quality loss
* Sources: `s04_p03`, `s04_p05`

### Real-time prediction-quality monitoring

* Good, because Tracks observed quality
* Good, because Connects to outcomes
* Bad, because Needs labels
* Bad, because Quality signal may be delayed
* Sources: `s01_p06`
