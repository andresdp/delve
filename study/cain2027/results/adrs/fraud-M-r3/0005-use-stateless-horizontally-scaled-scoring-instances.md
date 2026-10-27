# Use stateless horizontally scaled scoring instances

* System: Card-fraud scoring service

## Context and Problem Statement

The service must keep working during peaks. Independent request handling allows capacity to grow by adding serving instances.

## Decision Drivers

* Peak availability
* Horizontal scaling
* Request independence

## Considered Options

* Stateless horizontally scaled serving (`v:25.1`)
* Asynchronous message-driven serving (`v:25.2`)

## Decision Outcome

Chosen option: "Stateless horizontally scaled serving" (`v:25.1`).

Authorization needs an immediate score, while peak capacity benefits from independent replicas. The cited production architecture sources describe stateless serving that can scale horizontally.

### Consequences

* Keep per-request state outside serving instances.
* Provide capacity controls and health checks.

## Pros and Cons of the Options

### Stateless horizontally scaled serving

* Good, because Independent request handling
* Good, because Scales by adding replicas
* Bad, because Shared state needs separate storage
* Sources: `s01_p02`, `s04_p01`

### Asynchronous message-driven serving

* Good, because Decouples downstream work
* Good, because Buffers queued work
* Bad, because Does not directly return an immediate score
