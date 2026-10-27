# Forecast weekly demand per store and product

* System: Retail demand forecasting

## Context and Problem Statement

The system must produce retailer demand forecasts, and the brief specifies the forecast grain and cadence.

## Decision Drivers

* Weekly forecasts
* Store and product grain

## Considered Options

* Weekly forecasts per store and product
* Weekly forecasts per product across all stores

## Decision Outcome

Chosen option: "Weekly forecasts per store and product".

This directly matches the required forecast unit and cadence.

### Consequences

* Outputs need store and product identifiers.
* The forecast horizon remains unspecified.

## Pros and Cons of the Options

### Weekly forecasts per store and product

* Good, because Matches stated grain
* Good, because Supports weekly planning
* Bad, because Requires store-product inputs
* Bad, because May yield sparse series

### Weekly forecasts per product across all stores

* Good, because Fewer forecast series
* Good, because Simpler aggregation
* Bad, because Loses store variation
* Bad, because Does not match brief
