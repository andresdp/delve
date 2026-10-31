# Write scheduled forecasts to data storage

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly forecasts per store and product. The design space describes batch serving that writes predictions to storage, matching this output pattern (d:5).

## Decision Drivers

* Weekly output
* Store and product forecasts

## Considered Options

* Data batch based model serving (`v:5.3`)
* Precompute serving (`v:5.4`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving can calculate the weekly forecasts and write them to storage for downstream consumers (d:5, v:5.3).

### Consequences

* Define a stable forecast output schema.
* Publish each result with its forecast week and model version.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Fits scheduled forecasts
* Good, because Persists prediction results
* Bad, because Results refresh in batches
* Bad, because Consumers need storage access
* Sources: `d:5`, `v:5.3`

### Precompute serving

* Good, because Delivers prepared forecasts
* Good, because Supports report consumption
* Bad, because Requires report delivery design
* Bad, because Less suited to on-demand queries
* Sources: `d:5`, `v:5.4`

### Microservice based model serving

* Good, because Supports real-time queries
* Good, because Separates serving interface
* Bad, because Adds service operations
* Bad, because No real-time need stated
* Sources: `d:5`, `v:5.1`
