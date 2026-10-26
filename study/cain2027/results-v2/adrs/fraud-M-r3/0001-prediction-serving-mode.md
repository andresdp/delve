# Prediction serving mode

* System: Card-fraud scoring service

## Context and Problem Statement

Every transaction must receive its score before authorization, so predictions must be computed during the request. The scoring path also needs capacity for peak traffic.

## Decision Drivers

* Latency: tens of milliseconds
* Availability: peak traffic

## Considered Options

* Online computation serving (`v:31.5`)
* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Online computation serving" (`v:31.5`).

The authorization deadline makes request-time scoring decisive; scheduled batch scoring cannot meet it. This gives up the decoupling batch processing offers and requires the online path to remain available.

### Consequences

* Keep prediction computation on the authorization path.
* Live serving capacity must be available when transactions arrive.

## Pros and Cons of the Options

### Online computation serving

* Good, because Latency: scores current transaction context
* Good, because Availability: supports request-time scoring
* Bad, because Availability: each request depends on live serving capacity
* Sources: `s02_p02`, `s02_p13`, `s04_p10`

### Queue-fronted online serving cluster

* Good, because Availability: distributes work across predictors
* Good, because Latency: supports low-latency serving
* Bad, because Latency: queueing can add delay
* Sources: `s02_p11`, `s02_p13`, `s12_p07`

### Scheduled batch prediction deployment

* Good, because Availability: scores large sets on a schedule
* Good, because Latency: avoids request-time model computation
* Bad, because Latency: cannot score each transaction before authorization
* Sources: `s01_p08`, `s02_p12`, `s12_p02`
