# How to deploy model versions?

* System: Card-fraud scoring service

## Context and Problem Statement

The scoring record must identify its model version, and releases must preserve service continuity. The design space includes simultaneous versions and a single production model (d:10).

## Decision Drivers

* model version audit
* continuous scoring

## Considered Options

* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "N versions in production" (`v:10.1`).

Running multiple versions allows a new model to be staged while the current scorer remains available; log the exact version used for every transaction (d:10, d:22).

### Consequences

* Attach immutable version identifiers to scores.
* Manage routing and capacity per active version.

## Pros and Cons of the Options

### N versions in production

* Good, because Supports staged rollout
* Good, because Keeps versions addressable
* Bad, because More runtime complexity
* Bad, because Requires version routing
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simple routing
* Good, because Less runtime overhead
* Bad, because No concurrent comparison
* Bad, because Switching risk
* Sources: `d:10`, `v:10.3`
