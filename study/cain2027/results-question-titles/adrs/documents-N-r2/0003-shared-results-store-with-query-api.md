# Shared results store with query API

*How should teams consume classifications?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams use the classification results, so results should be accessible without requiring each consumer to call the classifier directly. The brief does not specify whether teams need push delivery, queries, or both.

## Decision Drivers

* Several consuming teams
* Millions daily
* Shared results

## Considered Options

* Shared results store with query API
* Publish results to a shared event stream

## Decision Outcome

Chosen option: "Shared results store with query API".

A shared store and API provide a common access point for multiple teams; the brief does not establish a need for event-driven delivery.

### Consequences

* The results schema becomes a shared contract.
* Access controls and query capacity need design.

## Pros and Cons of the Options

### Shared results store with query API

* Good, because Common source of truth
* Good, because Supports varied consumers
* Bad, because Adds API and storage operations
* Bad, because Consumers may see results later

### Publish results to a shared event stream

* Good, because Supports independent consumers
* Good, because Low coupling
* Bad, because Requires consumer coordination
* Bad, because Replay and retention need design
