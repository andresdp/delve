# Use a shared forecasting model across stores and products

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts demand at store and product level, but the brief gives no evidence that each combination has enough history for an independent model.

## Decision Drivers

* Store and product forecasts
* Three-person team
* Fast model iteration

## Considered Options

* Shared model across combinations
* Separate model per combination

## Decision Outcome

Chosen option: "Shared model across combinations".

A shared model is a practical starting point for a small team and can use store and product identity or attributes to distinguish combinations.

### Consequences

* Model features must identify stores and products.
* Evaluate performance across combinations for uneven fit.

## Pros and Cons of the Options

### Shared model across combinations

* Good, because Pools available history
* Good, because One model to operate
* Bad, because May miss local patterns
* Bad, because Requires combination features

### Separate model per combination

* Good, because Combination-specific fit
* Good, because Independent tuning
* Bad, because Many models to maintain
* Bad, because Sparse histories risk weak fits
