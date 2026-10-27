# Serve forecasts as scheduled batch outputs

* System: Retail demand forecasting

## Context and Problem Statement

The required output is a weekly forecast per store and product; the brief specifies no real-time prediction interface. The design space includes scheduled batch serving and precomputed forecast delivery (d:5).

## Decision Drivers

* Weekly output cadence
* Past-week forecast availability

## Considered Options

* Data batch based model serving (`v:5.3`)
* Precompute serving (`v:5.4`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Scheduled batch serving directly represents processing forecasts on schedule and writing them to storage. It fits weekly outputs and allows the system to retain forecast results for prior weeks.

### Consequences

* Persist each week's forecast outputs.
* Define storage and lookup conventions for consumers.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Writes scheduled forecasts to storage
* Good, because Matches weekly cadence
* Bad, because No immediate on-demand result
* Sources: `d:5`, `v:5.3`

### Precompute serving

* Good, because Delivers forecasts as reports
* Bad, because Requires report delivery details
* Sources: `d:5`, `v:5.4`

### Microservice based model serving

* Good, because Supports real-time requests
* Bad, because Unneeded service operations
* Sources: `d:5`, `v:5.1`
