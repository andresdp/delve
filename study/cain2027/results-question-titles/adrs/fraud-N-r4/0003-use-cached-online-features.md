# Use cached online features

*How should features reach inference?*

* System: Card-fraud scoring service

## Context and Problem Statement

The brief requires auditors to identify which features produced each score, while scoring must remain fast. Feature retrieval and the recorded feature snapshot both affect latency and later traceability.

## Decision Drivers

* Tens-of-milliseconds latency
* Feature provenance

## Considered Options

* Retrieve features online per request
* Compute features in the scoring service
* Use cached online features

## Decision Outcome

Chosen option: "Use cached online features".

A low-latency online lookup is a reasonable fit for the response target, provided the exact values used are captured for audit. The brief does not establish freshness needs, so cache policy remains an open design detail.

### Consequences

* Feature freshness and cache updates need defined policies.
* The score record must preserve the resolved feature values.

## Pros and Cons of the Options

### Retrieve features online per request

* Good, because Uses current data
* Good, because Central feature definitions
* Bad, because Adds retrieval latency
* Bad, because Adds data-service dependency

### Compute features in the scoring service

* Good, because Avoids feature-store hop
* Good, because Direct control of inputs
* Bad, because Duplicates feature logic
* Bad, because May lack latest signals

### Use cached online features

* Good, because Fast lookup
* Good, because Shared feature values
* Bad, because Can be stale
* Bad, because Requires cache consistency
