# Testing trained model quality

*What should be tested before a model is used?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without breaking the weekly forecast run, so training outputs need quality checks before release.

## Decision Drivers

* Protect weekly run
* Model quality
* Fast iteration

## Considered Options

* Testing trained model quality (`v:26.9`)
* Unit testing feature engineering logic (`v:26.6`)
* System integration testing (`v:26.5`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Quality testing provides a release gate for candidate models; the selected design point had no warnings, while the no-testing rival also had none, so the choice follows the brief's reliability requirement rather than source evidence.

### Consequences

* The team must define acceptance criteria for forecast quality.
* A candidate that fails the gate does not replace the production model.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Checks candidate forecast quality
* Good, because Can gate promotion
* Bad, because Needs agreed quality criteria
* Sources: `d:26`, `v:26.9`

### Unit testing feature engineering logic

* Good, because Finds transformation errors
* Bad, because Does not assess forecast quality
* Sources: `d:26`, `v:26.6`

### System integration testing

* Good, because Checks integrated workflow
* Bad, because Does not establish model quality
* Sources: `d:26`, `v:26.5`

### No testing

* Bad, because Changes can degrade forecasts unnoticed
* Sources: `d:26`, `v:26.14`
