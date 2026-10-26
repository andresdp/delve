# Data batch based model serving

*How should prediction results be served?*

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume classification results, and the brief does not require synchronous responses. The design space includes batch serving that writes results to storage and real-time service options (d:5).

## Decision Drivers

* Millions of documents/day
* Seasonal volume
* Several consuming teams

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Daily volume and multiple consumers favor batch output in shared storage; this gives up immediate prediction availability, which the brief does not require.

### Consequences

* Consumers need access to the result store.
* Batch completion becomes an availability dependency.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Throughput: process documents in scheduled batches
* Good, because Consumers: write results to shared storage
* Bad, because Latency: consumers wait for batch output
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Latency: return predictions in real time
* Bad, because Cost: maintain service capacity through demand changes
* Sources: `d:5`, `v:5.1`
