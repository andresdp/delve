# What is the forecast grain?

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand for each store and product. That grain defines the output key and the units the pipeline must produce.

## Decision Drivers

* Weekly forecasts
* Store/product coverage

## Considered Options

* Store × product × week
* Product × week across stores

## Decision Outcome

Chosen option: "Store × product × week".

It directly matches the brief’s stated forecast grain and preserves store-level demand information.

### Consequences

* Outputs are keyed by store, product, and week.
* Pipeline must handle the number of resulting series.

## Pros and Cons of the Options

### Store × product × week

* Good, because Matches stated requirement
* Good, because Directly actionable
* Bad, because Potentially many series

### Product × week across stores

* Good, because Fewer forecast series
* Good, because Simpler output
* Bad, because Loses store-level demand
