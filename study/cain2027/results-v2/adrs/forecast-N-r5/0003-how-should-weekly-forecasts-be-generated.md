# How should weekly forecasts be generated?

* System: Retail demand forecasting

## Context and Problem Statement

The system forecasts weekly demand for each store and product. This fits a scheduled batch run; the brief does not call for interactive predictions.

## Decision Drivers

* Protect weekly run
* Small team operations

## Considered Options

* Scheduled batch forecasting
* Online prediction service

## Decision Outcome

Chosen option: "Scheduled batch forecasting".

The weekly cadence decides the choice: scheduled batch generation avoids operating a service, while requiring recovery handling when a run fails.

### Consequences

* The run needs a schedule and failure recovery process.
* Forecast output delivery and consumers remain to be specified.

## Pros and Cons of the Options

### Scheduled batch forecasting

* Good, because Protect weekly run: produces a bounded weekly run
* Good, because Small team operations: avoids always-on serving
* Bad, because Protect weekly run: a failed run needs recovery handling

### Online prediction service

* Good, because Protect weekly run: predictions are available on demand
* Bad, because Small team operations: adds always-on service operations
