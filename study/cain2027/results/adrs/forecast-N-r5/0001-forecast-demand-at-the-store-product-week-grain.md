# Forecast demand at the store–product–week grain

* System: Retail demand forecasting

## Context and Problem Statement

The retailer’s stated forecast unit is weekly demand per store and product. Keeping this grain explicit gives the pipeline a consistent input and output contract.

## Decision Drivers

* Weekly forecasts
* Store–product detail

## Considered Options

* Store–product–week forecasts
* Aggregate by store or product

## Decision Outcome

Chosen option: "Store–product–week forecasts".

It directly matches the brief’s required forecast unit and avoids introducing an unstated allocation step.

### Consequences

* Pipeline inputs and outputs use this grain.
* Sparse or new series need a defined fallback.

## Pros and Cons of the Options

### Store–product–week forecasts

* Good, because Matches stated unit
* Good, because Directly actionable
* Bad, because Many individual series

### Aggregate by store or product

* Good, because Fewer series
* Good, because Simpler modeling
* Bad, because Loses detail
* Bad, because Needs allocation later
