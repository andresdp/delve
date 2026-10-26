# How should incoming documents be scored?

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents per day, and volume changes seasonally. The brief does not specify a response-time target.

## Decision Drivers

* High throughput
* Seasonal volume
* Shared results

## Considered Options

* Queue-fronted online serving cluster (`v:31.1`)
* Scheduled batch prediction deployment (`v:31.3`)

## Decision Outcome

Chosen option: "Queue-fronted online serving cluster" (`v:31.1`).

High throughput decides the choice: the queue distributes scoring across predictors and absorbs bursts, as described in “Architecting a Machine Learning Pipeline” and “System Architectures for Personalization and Recommendation.” This gives up batch simplicity; the brief does not establish a latency target.

### Consequences

* Operate a queue and scale predictor capacity with backlog.
* Persist results for multiple consuming teams.

## Pros and Cons of the Options

### Queue-fronted online serving cluster

* Good, because High throughput: queue distributes scoring load
* Good, because Seasonal volume: buffers demand spikes
* Bad, because Shared results: requires a separate results store
* Sources: `s02_p11`, `s02_p13`, `s12_p07`

### Scheduled batch prediction deployment

* Good, because High throughput: scores documents in batches
* Good, because Shared results: writes results to storage
* Bad, because Seasonal volume: batch capacity must be scheduled
* Bad, because Freshness: results wait for the next run
* Sources: `s01_p08`, `s02_p02`, `s12_p02`
