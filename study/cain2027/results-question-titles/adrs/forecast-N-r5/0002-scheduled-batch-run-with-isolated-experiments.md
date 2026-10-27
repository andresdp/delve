# Scheduled batch run with isolated experiments

*How should weekly runs be scheduled and isolated?*

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are produced weekly, and new model ideas must not break the weekly run. The pipeline needs a predictable run boundary and a way to keep experiments from disrupting it.

## Decision Drivers

* Weekly run
* Safe experimentation
* Small team

## Considered Options

* Scheduled batch run with isolated experiments
* Continuous retraining and deployment

## Decision Outcome

Chosen option: "Scheduled batch run with isolated experiments".

A scheduled batch aligns with the stated cadence, while isolating experiments protects the production run.

### Consequences

* The weekly run needs an explicit schedule and status tracking.
* Experimental models require a promotion path into production.

## Pros and Cons of the Options

### Scheduled batch run with isolated experiments

* Good, because Fits weekly cadence
* Good, because Separates experiments
* Bad, because Requires run monitoring
* Bad, because Needs promotion steps

### Continuous retraining and deployment

* Good, because Frequent updates
* Good, because Fewer scheduled jobs
* Bad, because Higher operational churn
* Bad, because Can disrupt weekly output
