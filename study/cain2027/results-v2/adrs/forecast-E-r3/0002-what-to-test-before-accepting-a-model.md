# What to test before accepting a model

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. The design space includes model quality tests and no testing (d:26).

## Decision Drivers

* Protect weekly run
* Production speed

## Considered Options

* Testing trained model quality (`v:26.9`)
* Unit testing feature engineering logic (`v:26.6`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Protecting the weekly run decides the choice: evaluate candidate model quality before release, accepting added evaluation work. The design point returned no warnings, while the rival combination with no testing did too; neither point had attesting sources.

### Consequences

* Define quality checks for candidate forecasts before release.
* Account for evaluation time in the model delivery workflow.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Protect weekly run: checks model quality
* Bad, because Production speed: adds evaluation work
* Sources: `d:26`, `v:26.9`

### Unit testing feature engineering logic

* Good, because Protect weekly run: catches feature logic errors
* Bad, because Production speed: requires maintained tests
* Sources: `d:26`, `v:26.6`

### No testing

* Good, because Production speed: no test delay
* Bad, because Protect weekly run: regressions may pass unnoticed
* Sources: `d:26`, `v:26.14`
