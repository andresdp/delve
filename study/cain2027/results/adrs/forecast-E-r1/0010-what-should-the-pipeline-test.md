# What should the pipeline test?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without breaking the existing weekly run.

## Decision Drivers

* Safe changes
* Forecast quality

## Considered Options

* Testing trained model quality (`v:26.9`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Quality testing provides a release check for new models before they affect weekly forecasts (d:26, v:26.9).

### Consequences

* The team must set model quality thresholds.
* Release automation must enforce the checks.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Checks forecast quality
* Good, because Can gate model release
* Bad, because Requires acceptance criteria
* Sources: `d:26`, `v:26.9`

### No testing

* Good, because No test maintenance
* Bad, because Regressions can reach production
* Sources: `d:26`, `v:26.14`
