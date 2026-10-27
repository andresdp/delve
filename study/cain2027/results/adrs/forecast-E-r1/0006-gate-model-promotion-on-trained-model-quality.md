# Gate model promotion on trained model quality

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires new model ideas to reach production without breaking a recurring forecast run. The design space includes tests of model quality, component behavior, and deployment strategies.

## Decision Drivers

* Protect weekly run
* Model iteration

## Considered Options

* Testing trained model quality (`v:26.9`)
* Unit testing feature engineering logic (`v:26.6`)
* Canary testing (`v:26.1`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Assessing candidate model quality directly addresses whether a new model is suitable for production. The design point used canary testing as a rival; neither checked point produced warnings or source attestations.

### Consequences

* Define forecast quality measures and promotion thresholds.
* Run quality checks before production promotion.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Screens candidate forecasts
* Good, because Supports promotion decisions
* Bad, because Needs agreed quality thresholds
* Sources: `d:26`, `v:26.9`

### Unit testing feature engineering logic

* Good, because Catches transformation defects
* Bad, because Does not assess forecast quality
* Sources: `d:26`, `v:26.6`

### Canary testing

* Good, because Limits initial exposure
* Bad, because Requires routing and comparison
* Sources: `d:26`, `v:26.1`
