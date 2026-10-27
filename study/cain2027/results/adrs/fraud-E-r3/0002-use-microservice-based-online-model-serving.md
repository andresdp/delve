# Use microservice based online model serving

* System: Card-fraud scoring service

## Context and Problem Statement

Fraud scores must be returned synchronously during authorization. Batch serving cannot meet that request path.

## Decision Drivers

* Online scoring
* Tens of milliseconds
* Peak traffic

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

This option explicitly serves scores in real time and can scale as a distributed service, matching the synchronous authorization path. The design point returned no warnings; its combination was unattested.

### Consequences

* Protect the request path from service latency and failures.
* Capacity must cover peak transaction volume.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Real-time scoring
* Good, because Independent scaling
* Bad, because Network dependency
* Bad, because Service operations
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Avoids remote call
* Good, because Lower network overhead
* Bad, because Closer deployment coupling
* Bad, because Scaling may be constrained
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Efficient bulk processing
* Good, because Scheduled workload
* Bad, because Not synchronous
* Bad, because Scores may be stale
* Sources: `d:5`, `v:5.3`
