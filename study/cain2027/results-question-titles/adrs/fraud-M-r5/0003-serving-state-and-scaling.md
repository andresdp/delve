# Serving state and scaling

* System: Card-fraud scoring service

## Context and Problem Statement

Scoring must continue during peaks, and the design point must choose a runtime state approach after defining the serving interface.

## Decision Drivers

* Peak availability
* Low response latency
* Horizontal capacity

## Considered Options

* Stateless horizontally scaled serving (`v:25.1`)
* Horizontally scaled Redis-backed asynchronous serving (`v:25.3`)

## Decision Outcome

Chosen option: "Stateless horizontally scaled serving" (`v:25.1`).

Choose independent serving replicas to absorb request peaks while keeping request handling simple. “Productionizing Machine Learning with a Microservices Architecture” supports stateless scaling; the alternative’s asynchronous queueing is a poor fit for a synchronous authorization response.

### Consequences

* Replicas must load a consistent model version.
* Shared feature state requires a separate store.

## Pros and Cons of the Options

### Stateless horizontally scaled serving

* Good, because Independent request handling
* Good, because Scale by adding replicas
* Bad, because Shared state belongs elsewhere
* Bad, because Replicas need consistent model versions
* Sources: `s01_p02`, `s04_p01`

### Horizontally scaled Redis-backed asynchronous serving

* Good, because Combines scaling and shared storage
* Good, because Asynchronous work decouples components
* Bad, because Adds Redis dependency
* Bad, because Asynchronous flow can delay response
