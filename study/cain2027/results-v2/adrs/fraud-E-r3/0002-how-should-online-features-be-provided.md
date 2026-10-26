# How should online features be provided?

* System: Card-fraud scoring service

## Context and Problem Statement

The scorer needs the features used for each transaction, and auditors must later identify which features produced each score.

## Decision Drivers

* Score latency
* Feature traceability

## Considered Options

* Feature store (`v:4.1`)
* Store features in data stores without specific support (`v:4.2`)

## Decision Outcome

Chosen option: "Feature store" (`v:4.1`).

Feature traceability decides: a central feature access layer gives a clear place to identify and retrieve scoring inputs. We accept its added dependency and must keep reads fast and available.

### Consequences

* Record the feature values or an immutable reference with each score.
* Feature-store availability becomes part of the online scoring path.

## Pros and Cons of the Options

### Feature store

* Good, because Feature traceability: central feature access
* Bad, because Score latency: added service dependency
* Sources: `d:4`, `v:4.1`

### Store features in data stores without specific support

* Good, because Score latency: direct access can be simple
* Bad, because Feature traceability: scattered feature definitions
* Sources: `d:4`, `v:4.2`
