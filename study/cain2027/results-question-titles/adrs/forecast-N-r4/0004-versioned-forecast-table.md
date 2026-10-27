# Versioned forecast table

*How should forecasts be published for consumers?*

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires forecasts but does not specify downstream consumers or interfaces. A durable, versioned output gives the weekly pipeline a clear handoff while preserving its history.

## Decision Drivers

* weekly output
* historical reproducibility
* unspecified consumers

## Considered Options

* Versioned forecast table
* Overwrite latest forecast file
* Consumer-specific API

## Decision Outcome

Chosen option: "Versioned forecast table".

A versioned table can preserve forecasts by week, store, product, and run, supporting both consumption and historical replay. The brief gives no evidence for an API or a particular file-based handoff.

### Consequences

* Agree on forecast keys and schema with consumers.
* Publish atomically when a run succeeds.
* Define access and retention policies.

## Pros and Cons of the Options

### Versioned forecast table

* Good, because queryable history
* Good, because clear run linkage
* Bad, because schema ownership needed
* Bad, because consumer access needed

### Overwrite latest forecast file

* Good, because simple handoff
* Good, because low setup
* Bad, because history can be lost
* Bad, because partial writes possible

### Consumer-specific API

* Good, because tailored access
* Good, because supports live queries
* Bad, because more service operations
* Bad, because consumer needs unknown
