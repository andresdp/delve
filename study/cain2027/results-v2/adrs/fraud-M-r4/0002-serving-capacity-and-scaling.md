# Serving capacity and scaling

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring runs in the authorization path, and the service must remain available during peaks. Capacity reduction to zero risks cold-start delay.

## Decision Drivers

* Peak availability
* Tens-of-milliseconds scoring

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)
* Replicated mutable model instances (`v:26.4`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Peak availability decides in favor of elastic capacity. This gives up some cost efficiency to avoid relying on scale-to-zero for an authorization-time request.

### Consequences

* Set capacity and scaling limits against observed peak traffic.
* Monitor latency and resource use as load changes.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Peak availability: capacity tracks demand
* Good, because Latency: scales out for load
* Bad, because Cost: extra peak capacity
* Sources: `s02_p01`, `s04_p02`

### Scale-to-zero serving

* Good, because Cost: removes idle capacity
* Bad, because Latency: cold start on demand
* Bad, because Availability: no warm capacity

### Replicated mutable model instances

* Good, because Peak availability: multiple instances
* Bad, because Availability: shared mutable state complicates operation
