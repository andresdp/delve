# Model in batch prediction system

*How should the classifier integrate with the application?*

* System: Large-scale document classification

## Context and Problem Statement

Millions of documents arrive daily, and several teams consume classifications. A batch prediction system can process large workloads while keeping classification separate from consuming applications.

## Decision Drivers

* Millions per day
* Multiple consumers
* Seasonal volume

## Considered Options

* Model in batch prediction system (`v:1.4`)
* Model as a service (`v:1.1`)

## Decision Outcome

Chosen option: "Model in batch prediction system" (`v:1.4`).

The brief emphasizes very high, seasonal volume and does not require immediate results. The batch option fits that workload; the real-time service rival is less directly supported by the stated needs. The checked combination is novel in the design space (`attested_by` is empty).

### Consequences

* Consumers retrieve results after processing completes.
* Batch capacity must scale with seasonal demand.

## Pros and Cons of the Options

### Model in batch prediction system

* Good, because Separates consumers from prediction
* Good, because Fits batch workloads
* Bad, because Results are not immediate
* Sources: `d:1`, `v:1.4`

### Model as a service

* Good, because Reusable by teams
* Good, because Direct integration
* Bad, because Service capacity must handle peaks
* Sources: `d:1`, `v:1.1`
