# Run demand forecasting as a weekly batch pipeline

* System: Retail demand forecasting

## Context and Problem Statement

The system produces forecasts at weekly store-and-product granularity. A scheduled batch run fits that cadence.

## Decision Drivers

* Weekly forecast cadence
* Store-product granularity

## Considered Options

* Scheduled batch pipeline
* Continuous streaming forecasts

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

Weekly batch execution fits the required forecast cadence and keeps operations manageable for a three-person team.

### Consequences

* Forecasts update on the weekly schedule.
* The pipeline needs a defined run schedule.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Matches weekly cadence
* Good, because Simple operations
* Bad, because Not real time

### Continuous streaming forecasts

* Good, because Low-latency updates
* Bad, because More operational complexity
* Bad, because Exceeds stated cadence
