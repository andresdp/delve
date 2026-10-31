# Retrain when quality or data shifts cross thresholds

* System: Card-fraud scoring service

## Context and Problem Statement

Changes in data or model quality can make deployed fraud scores less useful. Retraining should follow measured signals rather than an unspecified cadence.

## Decision Drivers

* Model quality
* Data changes
* Controlled updates

## Considered Options

* Threshold-based retraining (`v:6.3`)
* Schedule-based retraining trigger (`v:6.6`)

## Decision Outcome

Chosen option: "Threshold-based retraining" (`v:6.3`).

A threshold trigger connects retraining to observed quality or input changes, while schema anomalies can stop the process for investigation. MLOps: Continuous Delivery and Automation Pipelines in Machine Learning supports threshold-driven adaptation.

### Consequences

* Calibrate triggers against labeled outcomes.
* Require review before promoting a retrained model.

## Pros and Cons of the Options

### Threshold-based retraining

* Good, because Responds to measured shifts
* Good, because Can halt on schema anomalies
* Bad, because Thresholds need calibration
* Sources: `s06_p08`, `s20_p03`

### Schedule-based retraining trigger

* Good, because Predictable retraining cadence
* Bad, because May miss sudden drift
