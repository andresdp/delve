# Monitor input and feature drift in production

* System: Retail demand forecasting

## Context and Problem Statement

Weekly forecasts can become unreliable as retail inputs change. The brief gives no requirement for fully automatic retraining, so drift monitoring provides visibility without assuming retraining policy.

## Decision Drivers

* Forecast reliability
* Weekly operation
* Small team

## Considered Options

* Input and feature-drift monitoring (`v:6.2`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Input and feature-drift monitoring" (`v:6.2`).

Choose drift monitoring to surface changes in schemas and feature distributions that could affect weekly forecasts. “Machine Learning Monitoring: What It Is, and What We Are Missing” and “MLOps Principles” describe monitoring these changes.

### Consequences

* Monitoring signals need review and response ownership.
* Drift alerts alone do not establish forecast degradation.

## Pros and Cons of the Options

### Input and feature-drift monitoring

* Good, because Detects changing inputs
* Good, because Supports investigation
* Bad, because Requires drift thresholds
* Bad, because Drift may not mean quality loss
* Sources: `s04_p03`, `s04_p05`, `s04_p12`, `s06_p02`, `s06_p08`, `s20_p03`, `s21_p10`, `s22_p11`, `s23_p03`, `s23_p04`, `s23_p05`, `s24_p01`, `s24_p07`, `s24_p08`, `s24_p11`, `s25_p01`

### Passive production operation

* Good, because Low operating overhead
* Good, because No alert tuning
* Bad, because Problems may go unseen
* Bad, because No drift visibility
* Sources: `s13_p10`, `s21_p07`, `s23_p13`
