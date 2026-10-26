# How should the LLM classifier be invoked?

* System: Large-scale document classification

## Context and Problem Statement

Classification relies on an LLM, and the system must sustain high daily volume. The serving approach affects throughput, scaling, and operational control.

## Decision Drivers

* LLM classifier
* millions per day
* seasonal volume

## Considered Options

* External hosted LLM API
* Self-hosted model endpoint

## Decision Outcome

Chosen option: "External hosted LLM API".

A hosted endpoint avoids operating model-serving infrastructure; queued, autoscaled workers can regulate request volume.

### Consequences

* Provider quotas and availability constrain throughput.
* Per-document inference costs need tracking.

## Pros and Cons of the Options

### External hosted LLM API

* Good, because managed inference
* Good, because quick model updates
* Bad, because provider dependency
* Bad, because cost and quota exposure

### Self-hosted model endpoint

* Good, because serving control
* Good, because capacity tuning
* Bad, because GPU operations
* Bad, because model maintenance
