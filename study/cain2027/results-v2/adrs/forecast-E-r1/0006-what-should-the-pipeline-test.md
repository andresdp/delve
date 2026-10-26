# What should the pipeline test?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must not break the weekly run; the design space offers tests for components, training, model quality, pipelines, and APIs (d:26).

## Decision Drivers

* Weekly run reliability
* Fast iteration
* Small team

## Considered Options

* Unit testing pipeline components (`v:26.10`)
* Integration testing pipeline components (`v:26.11`)
* Testing trained model quality (`v:26.9`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Integration testing pipeline components" (`v:26.11`).

Weekly run reliability decides the choice: validate that pipeline components work together before release, accepting some added test time; the design space permits combining this with component and model-quality tests.

### Consequences

* Run integration checks before production promotion.
* Define forecast-quality acceptance thresholds as a separate project requirement.

## Pros and Cons of the Options

### Unit testing pipeline components

* Good, because Fast iteration: catches component defects early
* Bad, because Weekly run reliability: does not validate the full workflow
* Sources: `d:26`, `v:26.10`

### Integration testing pipeline components

* Good, because Weekly run reliability: checks connected pipeline behavior
* Bad, because Fast iteration: broader tests can take longer
* Sources: `d:26`, `v:26.11`

### Testing trained model quality

* Good, because Weekly run reliability: checks forecast quality before release
* Bad, because Small team: requires defining quality thresholds
* Sources: `d:26`, `v:26.9`

### No testing

* Bad, because Weekly run reliability: defects can reach production
* Sources: `d:26`, `v:26.14`
