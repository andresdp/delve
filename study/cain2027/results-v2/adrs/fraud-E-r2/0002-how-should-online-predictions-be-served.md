# How should online predictions be served?

* System: Card-fraud scoring service

## Context and Problem Statement

The score must be available before authorization, ruling out scheduled batch output for the transaction decision. The design space describes real-time serving through distributed or local services (d:5).

## Decision Drivers

* Tens-of-milliseconds latency
* Peak availability

## Considered Options

* Microservice based model serving (`v:5.1`)
* Local service/API based model serving (`v:5.2`)
* Data batch based model serving (`v:5.3`)

## Decision Outcome

Chosen option: "Microservice based model serving" (`v:5.1`).

Peak availability decides: a distributed real-time service can scale separately as transaction demand rises. This accepts the network overhead that local serving avoids.

### Consequences

* Serving capacity must scale with transaction peaks.
* The authorization path depends on service availability.

## Pros and Cons of the Options

### Microservice based model serving

* Good, because Availability: scale serving independently
* Good, because Latency: supports real-time responses
* Bad, because Latency: distributed call overhead
* Sources: `d:5`, `v:5.1`

### Local service/API based model serving

* Good, because Latency: local call path
* Bad, because Availability: less independent scaling
* Sources: `d:5`, `v:5.2`

### Data batch based model serving

* Good, because Cost: scheduled bulk processing
* Bad, because Latency: unavailable before authorization
* Sources: `d:5`, `v:5.3`
