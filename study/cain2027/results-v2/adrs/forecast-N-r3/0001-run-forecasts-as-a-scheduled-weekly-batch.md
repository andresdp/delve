# Run forecasts as a scheduled weekly batch

* System: Retail demand forecasting

## Context and Problem Statement

The system produces demand forecasts once per week for each store and product. The brief gives no need for interactive or real-time predictions.

## Decision Drivers

* Weekly-run reliability
* Fast model iteration

## Considered Options

* Scheduled batch pipeline
* On-demand prediction service

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

Weekly-run reliability decides the choice: a scheduled batch matches the forecast cadence and keeps execution bounded. This gives up on-demand forecasts, which the brief does not require.

### Consequences

* Pipeline must complete within the weekly delivery window.
* Model changes must integrate with the batch run.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Weekly-run reliability: bounded, repeatable run
* Good, because Fast model iteration: changes fit pipeline stages
* Bad, because Weekly-run reliability: failures can delay the full run

### On-demand prediction service

* Good, because Fast model iteration: deploy behind a service
* Bad, because Weekly-run reliability: adds always-on service operations
* Bad, because Fast model iteration: requires serving integration
