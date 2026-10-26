# How should forecast results be served?

* System: Retail demand forecasting

## Context and Problem Statement

The system creates weekly forecasts, so consumers can use precomputed results rather than needing live model responses.

## Decision Drivers

* Weekly forecasts
* Store/product output
* Small team

## Considered Options

* Precompute serving (`v:5.4`)
* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Precompute serving" (`v:5.4`).

Precomputing forecasts suits the weekly reporting need and avoids operating a real-time prediction service (d:5, v:5.4).

### Consequences

* Consumers read stored forecast outputs.
* Forecasts become available after each run.

## Pros and Cons of the Options

### Precompute serving

* Good, because Fits forecast reports
* Good, because Avoids live serving
* Bad, because Results refresh by batch
* Sources: `d:5`, `v:5.4`

### Microservice based model serving

* Good, because Live responses
* Good, because Service interface
* Bad, because More components
* Bad, because Unneeded latency work
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because Scheduled batch output
* Good, because Writes to storage
* Bad, because Less suited to report delivery
* Sources: `d:5`, `v:5.3`
