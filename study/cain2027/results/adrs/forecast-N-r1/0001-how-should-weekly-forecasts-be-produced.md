# How should weekly forecasts be produced?

* System: Retail demand forecasting

## Context and Problem Statement

Demand is forecast weekly for each store and product. The pipeline needs a repeatable path from input data to forecasts.

## Decision Drivers

* Weekly cadence
* Store-product forecasts
* Reproducibility

## Considered Options

* Scheduled batch pipeline
* Online prediction service

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

A scheduled batch run matches the weekly forecast cadence and gives each forecast period a defined run that can be reproduced.

### Consequences

* Forecasts update on the weekly schedule.
* A failed run needs detection and rerun handling.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Fits weekly cadence
* Good, because Clear run boundaries
* Bad, because Results arrive on schedule
* Bad, because Requires orchestration

### Online prediction service

* Good, because On-demand forecasts
* Good, because Always available
* Bad, because Unneeded serving complexity
* Bad, because Harder to reproduce runs
