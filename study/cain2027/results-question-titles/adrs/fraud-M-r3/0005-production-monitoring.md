# Production monitoring

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring service must expose operational problems, and fraud patterns or transaction features may change after deployment.

## Decision Drivers

* Service availability
* Feature changes
* Auditability

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Monitor feature and schema changes to surface risks to live scoring. “Productionizing Machine Learning with a Microservices Architecture” and Google’s “MLOps: Continuous delivery and automation pipelines in machine learning” describe input and feature monitoring; the brief does not specify a retraining policy.

### Consequences

* Log and compare production feature statistics over time.
* Define alert thresholds and investigation ownership.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Detects schema and distribution changes
* Good, because Supports investigation
* Bad, because Drift alone does not establish model quality
* Sources: `s04_p03`, `s06_p02`

### Service-health and data-quality monitoring

* Good, because Covers latency and uptime
* Good, because Includes data quality
* Bad, because Needs model-specific signals
* Sources: `s04_p02`, `s06_p02`

### Passive production operation

* Good, because Low monitoring effort
* Bad, because No active failure visibility
* Bad, because Weak fit for availability needs
