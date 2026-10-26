# What should be tested before model delivery?

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces a candidate model for production cameras. The design space lists model quality testing and several software and pipeline testing options.

## Decision Drivers

* defect detection quality
* weekly retraining
* production delivery

## Considered Options

* Testing trained model quality (`v:26.9`)
* Canary testing (`v:26.1`)
* Unit testing system components (`v:26.4`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Testing candidate model quality directly supports the requirement to detect defects on production lines. The checked combination had no warnings, but no attesting sources.

### Consequences

* Set acceptance criteria for each candidate model.
* Retain representative labelled images for evaluation.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because checks candidate quality
* Bad, because quality criteria must be defined
* Sources: `d:26`, `v:26.9`

### Canary testing

* Good, because limits initial exposure
* Bad, because requires staged rollout
* Sources: `d:26`, `v:26.1`

### Unit testing system components

* Good, because checks component behavior
* Bad, because does not establish model quality
* Sources: `d:26`, `v:26.4`
