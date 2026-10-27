# Serve low-latency features from an online feature store

* System: Card-fraud scoring service

## Context and Problem Statement

The model needs transaction features at scoring time, and feature computation or remote lookups can consume the latency budget. An online store can supply precomputed features quickly.

## Decision Drivers

* Tens-of-milliseconds latency
* Consistent model inputs
* Peak availability

## Considered Options

* Online feature store
* Compute features in the scoring service
* Fetch features from source systems per request

## Decision Outcome

Chosen option: "Online feature store".

Precomputed features help meet the tight response-time requirement while keeping model inputs reusable. The online store must be kept sufficiently fresh and available.

### Consequences

* Feature freshness needs monitoring
* Store failures affect scoring

## Pros and Cons of the Options

### Online feature store

* Good, because Fast feature reads
* Good, because Reusable feature definitions
* Bad, because Requires fresh updates
* Bad, because Adds operational dependency

### Compute features in the scoring service

* Good, because Fewer services
* Good, because Direct access to request data
* Bad, because Repeats computation
* Bad, because May increase latency

### Fetch features from source systems per request

* Good, because Current source data
* Good, because Avoids feature replication
* Bad, because Many network calls
* Bad, because Source outages affect scoring
