# Serving capacity under peaks

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring service must continue working as transaction volume rises. The brief gives no traffic profile or cost target.

## Decision Drivers

* Availability: peaks
* Latency: tens of milliseconds

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Peak availability and low latency decide the choice: elastic capacity can meet changing load, while scale-to-zero risks startup delay. That gives up some potential idle-capacity savings. “Architecting a Machine Learning Pipeline” and “Productionizing Machine Learning with a Microservices Architecture” describe elastic scaling.

### Consequences

* Maintain scaling headroom for sudden peaks.
* Tune scaling behavior against observed latency and demand.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Availability: capacity follows workload demand
* Bad, because Latency: scale-up may lag sudden spikes
* Sources: `s02_p01`, `s04_p02`, `s13_p09`, `s21_p15`

### Scale-to-zero serving

* Good, because Cost: avoids idle serving capacity
* Bad, because Latency: cold start can delay scoring
* Sources: `s11_p04`, `s13_p09`
