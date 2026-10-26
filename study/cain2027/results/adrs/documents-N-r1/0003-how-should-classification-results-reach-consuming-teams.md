# How should classification results reach consuming teams?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classification results, so delivery should avoid coupling the classifier to each team's integration and availability.

## Decision Drivers

* Several consumers
* Independent team needs

## Considered Options

* Publish results to a shared event stream
* Call each consumer directly

## Decision Outcome

Chosen option: "Publish results to a shared event stream".

A shared stream lets several teams receive results without making classification dependent on their individual services. It also provides a buffer for consumers to process results at their own pace.

### Consequences

* Consumers need schemas and delivery guarantees.
* Stream retention and access need management.

## Pros and Cons of the Options

### Publish results to a shared event stream

* Good, because Supports multiple consumers
* Good, because Consumers progress independently
* Bad, because Requires event operations
* Bad, because Consumers must handle duplicates

### Call each consumer directly

* Good, because Direct delivery
* Good, because Simple for few consumers
* Bad, because Couples classifier to consumers
* Bad, because Consumer outages affect delivery
