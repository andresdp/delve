# Online score serving

* System: Card-fraud scoring service

## Context and Problem Statement

Each transaction must be scored before authorization, so precomputed or scheduled scores do not fit the request path.

## Decision Drivers

* Real-time scoring
* Low latency
* Peak traffic

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

This option explicitly supports real-time scores and allows serving capacity to scale separately during peaks. The brief makes latency a constraint, so network overhead must be budgeted and monitored.

### Consequences

* Replicate and scale the serving service for peak demand.
* Measure end-to-end scoring latency.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time distributed service
* Good, because Independent scaling
* Bad, because Network overhead
* Bad, because Service availability dependency
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Local call path
* Good, because Lower network overhead
* Bad, because Coupled capacity
* Bad, because Shared release concerns
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Efficient bulk processing
* Good, because Scheduled workloads
* Bad, because Not request-time
* Bad, because Stale transaction scores
* Sources: `d:5`, `v:5.3`
