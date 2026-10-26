# How should classifications be computed and delivered?

* System: Large-scale document classification

## Context and Problem Statement

The classifier processes millions of documents daily, and the brief gives no interactive latency requirement. Results must be consumed by several teams.

## Decision Drivers

* Millions of documents daily
* Multiple consuming teams

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Queue-fronted online serving cluster (`v:31.1`)

## Decision Outcome

Chosen option: "Scheduled batch prediction deployment" (`v:31.3`).

The daily volume and lack of a stated latency target favor batch scoring; the sources “Architecting a Machine Learning Pipeline” and “Three Levels of ML Software” describe scheduled batch deployment. This gives up immediate results, which the brief does not require.

### Consequences

* Teams consume persisted results after each scoring run.
* Define the scoring schedule and freshness expectations.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Volume: scores large workloads on a schedule
* Good, because Teams: writes results to shared storage
* Bad, because Freshness: results wait for the next run
* Sources: `s02_p02`, `s02_p12`, `s02_p13`, `s12_p02`, `s15_p04`, `s15_p05`, `s19_p14`, `s19_p16`, `s25_p06`

### Queue-fronted online serving cluster

* Good, because Freshness: scores as requests arrive
* Good, because Volume: queue distributes scoring load
* Bad, because Cost: keeps online serving capacity available
* Sources: `s02_p11`, `s02_p13`, `s12_p07`, `s19_p15`
