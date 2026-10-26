# How should LLM classification be served?

* System: Large-scale document classification

## Context and Problem Statement

Classification volume is high and varies seasonally. The brief requires an LLM-based classifier but does not specify whether it must run on a managed API or self-hosted infrastructure.

## Decision Drivers

* LLM-based classification
* Variable volume
* High throughput

## Considered Options

* Managed LLM endpoint
* Self-hosted model serving

## Decision Outcome

Chosen option: "Managed LLM endpoint".

A managed endpoint is a reasonable default for variable demand because it can reduce the effort of operating model capacity. Provider capacity, latency, data terms, and cost must be validated before implementation.

### Consequences

* The service depends on provider availability and limits.
* Usage-based costs need tracking.

## Pros and Cons of the Options

### Managed LLM endpoint

* Good, because Operationally simpler
* Good, because Elastic capacity may be available
* Bad, because Provider dependency
* Bad, because Usage costs vary

### Self-hosted model serving

* Good, because More control
* Good, because Potential cost predictability
* Bad, because Capacity operations burden
* Bad, because Scaling requires planning
