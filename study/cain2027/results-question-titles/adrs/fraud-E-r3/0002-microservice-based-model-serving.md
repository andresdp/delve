# Microservice based model serving

*How should online scores be served?*

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores must arrive within tens of milliseconds as part of authorization. This requires synchronous online inference rather than scheduled batch scoring.

## Decision Drivers

* tens of milliseconds
* synchronous authorization
* peak traffic

## Considered Options

* Microservice based model serving (`v:5.1`)
* Data batch based model serving (`v:5.3`)
* Local service/API based model serving (`v:5.2`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

A real-time service matches the authorization flow and can be scaled for peaks; its network call must be kept within the response budget. (d:5, v:5.1)

### Consequences

* Authorization depends on scoring-service availability.
* Capacity and latency need production monitoring.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because real-time scoring
* Good, because independent scaling
* Bad, because network overhead
* Bad, because service dependency
* Sources: `d:5`, `v:5.1`

### Data batch based model serving

* Good, because scheduled processing
* Good, because writes results to storage
* Bad, because not transaction synchronous
* Bad, because stale scores
* Sources: `d:5`, `v:5.3`

### Local service/API based model serving

* Good, because real-time scoring
* Good, because avoids remote model call
* Bad, because less independent scaling
* Bad, because tied to application runtime
* Sources: `d:5`, `v:5.2`
