# Monitor input and feature drift in production

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud patterns and transaction inputs can change after deployment. The brief also requires later identification of the features used for each score.

## Decision Drivers

* Changing fraud patterns
* Feature integrity
* Auditability

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Monitoring feature and input changes helps detect when deployed scoring inputs diverge from expectations. Productionizing Machine Learning with a Microservices Architecture and Machine Learning Monitoring describe monitoring of feature generation and input changes.

### Consequences

* Retain feature and schema observations.
* Define investigation and response thresholds.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Surfaces input changes
* Good, because Supports investigation
* Bad, because Requires baselines and alerts
* Sources: `s04_p03`, `s06_p02`, `s23_p03`

### Passive production operation

* Good, because Lower monitoring effort
* Bad, because Misses production changes
