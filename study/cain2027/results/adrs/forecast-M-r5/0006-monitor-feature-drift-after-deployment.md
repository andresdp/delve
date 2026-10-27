# Monitor feature drift after deployment

* System: Retail demand forecasting

## Context and Problem Statement

Demand patterns and inputs may change over time, affecting forecast quality. Monitoring input and feature changes provides a signal for investigation and future retraining.

## Decision Drivers

* Changing demand inputs
* Protect forecast quality
* Operational visibility

## Considered Options

* Passive production operation (`v:6.4`)
* Input and feature-drift monitoring (`v:6.2`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

The checked point includes this accepted option, although the point is unattested and warns that data ingestion remains undecided. “MLOps Principles” and “Productionizing Machine Learning with a Microservices Architecture” support monitoring feature and input changes; for a weekly forecast system, drift is a useful signal to investigate before changing models.

### Consequences

* Define baselines for monitored inputs.
* Drift alerts require review and may prompt retraining.

## Pros and Cons of the Options

### Passive production operation

* Good, because Low monitoring setup
* Good, because Low ongoing effort
* Bad, because No early drift signal
* Bad, because Failures may go unnoticed

### Input and feature-drift monitoring

* Good, because Surfaces data shifts
* Good, because Supports investigation
* Bad, because Requires baselines and thresholds
* Bad, because Does not prove quality loss alone
* Sources: `s04_p03`, `s06_p08`, `s22_p11`
