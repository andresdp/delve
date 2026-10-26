# Expose results through a shared results interface

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classifications, so a common result contract avoids making each team depend directly on classifier internals. The brief does not specify whether consumers need push or pull access.

## Decision Drivers

* Several consuming teams
* Millions of documents per day

## Considered Options

* Shared result store with documented API
* Publish results to each team separately

## Decision Outcome

Chosen option: "Shared result store with documented API".

Several consumers decide in favor of one shared contract; teams give up some delivery customization and must coordinate on schema changes.

### Consequences

* Define stable fields for class, confidence, and processing status.
* Consumer access patterns and freshness needs remain to be specified.

## Pros and Cons of the Options

### Shared result store with documented API

* Good, because Teams: common access contract
* Good, because Scale: decouples reads from inference
* Bad, because Teams: requires API and schema ownership

### Publish results to each team separately

* Good, because Teams: tailored delivery per consumer
* Bad, because Scale: duplicate distribution work
* Bad, because Teams: more integrations to maintain
