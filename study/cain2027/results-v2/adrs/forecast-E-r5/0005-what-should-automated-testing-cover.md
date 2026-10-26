# What should automated testing cover?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without breaking the weekly run. The system’s specific forecast quality thresholds are not stated.

## Decision Drivers

* Weekly run reliability
* Fast iteration
* Reproducibility

## Considered Options

* Unit testing feature engineering logic (`v:26.6`)
* Integration testing pipeline components (`v:26.11`)
* Testing trained model quality (`v:26.9`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Integration testing pipeline components" (`v:26.11`).

Weekly run reliability decides the choice: integration tests can catch failures across the pipeline before release. They add execution time, and the brief does not supply thresholds for model quality tests.

### Consequences

* Include pipeline integration checks in delivery gates.
* Define forecast quality thresholds separately.

## Pros and Cons of the Options

### Unit testing feature engineering logic

* Good, because Reproducibility: catches changed feature calculations
* Bad, because Weekly run reliability: misses failures across components
* Sources: `d:26`, `v:26.6`

### Integration testing pipeline components

* Good, because Weekly run reliability: checks components working together
* Bad, because Fast iteration: broader checks take longer than unit tests
* Sources: `d:26`, `v:26.11`

### Testing trained model quality

* Good, because Weekly run reliability: catches quality regressions
* Bad, because Fast iteration: needs agreed quality thresholds
* Sources: `d:26`, `v:26.9`

### No testing

* Good, because Fast iteration: no test development overhead
* Bad, because Weekly run reliability: regressions may go unnoticed
* Sources: `d:26`, `v:26.14`
