# Data batch based model serving

*How should forecasts be delivered?*

* System: Retail demand forecasting

## Context and Problem Statement

The output is a weekly forecast per store and product, which can be computed in batches and written to storage. No real-time client requirement appears in the brief.

## Decision Drivers

* Weekly output
* Reproducibility
* Small team

## Considered Options

* Data batch based model serving (`v:5.3`)
* Precompute serving (`v:5.4`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving matches the weekly output and keeps the serving path straightforward. The checked design point has no warnings and no attesting sources.

### Consequences

* Write forecast records to data storage after each run.
* Make each output traceable to its model and input versions.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Writes scheduled predictions to storage
* Good, because Matches weekly output
* Bad, because Not real time
* Sources: `d:5`, `v:5.3`

### Precompute serving

* Good, because Delivers precomputed forecasts
* Bad, because Requires report delivery path
* Sources: `d:5`, `v:5.4`

### Microservice based model serving

* Good, because Serves predictions in real time
* Bad, because Adds service operations
* Sources: `d:5`, `v:5.1`
