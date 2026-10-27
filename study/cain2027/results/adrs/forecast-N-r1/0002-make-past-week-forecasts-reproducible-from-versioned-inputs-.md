# Make past-week forecasts reproducible from versioned inputs and code

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires forecasts to be reproducible for any past week, which requires retaining enough information to reconstruct a run.

## Decision Drivers

* Past-week reproducibility
* End-to-end pipeline ownership

## Considered Options

* Version inputs, code, and run configuration
* Record forecast outputs only

## Decision Outcome

Chosen option: "Version inputs, code, and run configuration".

A saved output alone cannot reproduce a forecast; versioned run dependencies give the team a basis for replay.

### Consequences

* Historical data and code references must remain available.
* Retention duration and storage mechanism need definition.

## Pros and Cons of the Options

### Version inputs, code, and run configuration

* Good, because Supports historical replay
* Good, because Makes run provenance explicit
* Bad, because Requires artifact retention
* Bad, because Adds versioning work

### Record forecast outputs only

* Good, because Simple storage
* Good, because Easy to inspect past outputs
* Bad, because Cannot reconstruct runs
* Bad, because Weak debugging evidence
