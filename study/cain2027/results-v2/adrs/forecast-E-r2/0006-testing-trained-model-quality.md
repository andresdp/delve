# Testing trained model quality

*How to test pipeline changes?*

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must not break the weekly run, so the pipeline needs checks before production. The design space lists tests for model quality, components, and integration (d:26).

## Decision Drivers

* Protect weekly run
* Ship model ideas quickly
* Reproduce any past week

## Considered Options

* Testing trained model quality (`v:26.9`)
* Unit testing pipeline components (`v:26.10`)
* Integration testing pipeline components (`v:26.11`)
* No testing (`v:26.14`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Protecting the weekly run decides the choice: gate releases on forecast quality, accepting slower delivery while models are evaluated (d:26, v:26.9).

### Consequences

* Define an acceptance threshold for forecast quality.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Protect weekly run: catches degraded forecasts
* Bad, because Ship model ideas quickly: evaluation adds a gate
* Sources: `d:26`, `v:26.9`

### Unit testing pipeline components

* Good, because Ship model ideas quickly: fast component feedback
* Bad, because Protect weekly run: may miss end-to-end failures

### Integration testing pipeline components

* Good, because Protect weekly run: checks connected components
* Bad, because Ship model ideas quickly: slower feedback

### No testing

* Bad, because Protect weekly run: failures can reach production
