# Test model quality before release

* System: Retail demand forecasting

## Context and Problem Statement

The system must protect a recurring production run while accepting new model ideas. Testing trained model quality is an available pipeline test practice (d:26).

## Decision Drivers

* Release safety
* Forecast quality

## Considered Options

* Testing trained model quality (`v:26.9`)
* Unit testing feature engineering logic (`v:26.6`)
* Canary testing (`v:26.1`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Quality checks on trained models give the team a basis to reject candidates that could degrade forecasts (d:26, v:26.9). The checked point had no warnings; both the selected point and the rival were unattested, so the design-space check offers no attestation advantage.

### Consequences

* Define forecast quality thresholds outside the design space.
* Retain evaluation results with each model version.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Checks candidate forecasts
* Good, because Supports release gating
* Bad, because Needs quality criteria
* Bad, because Requires representative evaluation data
* Sources: `d:26`, `v:26.9`

### Unit testing feature engineering logic

* Good, because Catches transformation defects
* Good, because Fast feedback
* Bad, because Does not assess forecast quality
* Bad, because Requires maintained test cases
* Sources: `d:26`, `v:26.6`

### Canary testing

* Good, because Limits initial exposure
* Good, because Observes a candidate in production
* Bad, because Adds rollout complexity
* Bad, because May not suit batch output
* Sources: `d:26`, `v:26.1`
