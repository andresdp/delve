# What should be tested before accepting a model?

* System: Retail demand forecasting

## Context and Problem Statement

New models should not disrupt the production forecast run. The design space includes component tests and trained-model quality tests; these practices can be combined.

## Decision Drivers

* Protect weekly run
* Model quality
* Fast iteration

## Considered Options

* Test feature logic, pipeline components, and trained model quality
* System integration testing (`v:26.5`)
* Canary testing (`v:26.1`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Test feature logic, pipeline components, and trained model quality".

Combine feature and pipeline unit checks with trained-model quality tests to catch failures before promotion (d:26, v:26.6, v:26.10, v:26.9).

### Consequences

* Quality thresholds need agreement.
* Tests add time to candidate evaluation.

## Pros and Cons of the Options

### Test feature logic, pipeline components, and trained model quality

* Good, because Catches code and quality issues
* Good, because Works as release gate
* Bad, because Needs maintained checks
* Sources: `d:26`, `v:26.6`, `v:26.10`, `v:26.9`

### System integration testing

* Good, because Checks component interactions
* Bad, because May miss model quality
* Sources: `d:26`, `v:26.5`

### Canary testing

* Good, because Limits rollout exposure
* Bad, because Needs parallel operation
* Sources: `d:26`, `v:26.1`

### No testing

* Good, because Less setup
* Bad, because Run failures less contained
* Sources: `d:26`, `v:26.14`
