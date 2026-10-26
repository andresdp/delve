# Online score serving

* System: Card-fraud scoring service

## Context and Problem Statement

The score must return within tens of milliseconds, ruling out scheduled batch scoring for the authorization path. The design space distinguishes real-time serving options (d:5).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Peak availability decides in favor of distributed service serving, at the cost of a network hop that consumes latency budget. The checked combination had no warnings, but no sources attested it.

### Consequences

* The online service must fit within the end-to-end latency budget.
* Peak capacity depends on service scaling.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Peak availability: distributed service can scale
* Bad, because Low latency: network hop
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Low latency: local service call
* Bad, because Peak availability: less independent scaling
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Bad, because Low latency: scheduled batch cannot serve authorization-time scores
* Sources: `d:5`, `v:5.3`
