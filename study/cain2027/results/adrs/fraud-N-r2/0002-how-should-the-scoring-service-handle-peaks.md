# How should the scoring service handle peaks?

* System: Card-fraud scoring service

## Context and Problem Statement

The system must keep scoring transactions during peak load. The brief does not prescribe a deployment or scaling platform.

## Decision Drivers

* Peak availability
* Low latency

## Considered Options

* Stateless replicated service
* Single scoring instance

## Decision Outcome

Chosen option: "Stateless replicated service".

Replicated instances can add capacity for peaks and reduce dependence on any one scoring process.

### Consequences

* Instances need consistent model and feature access.
* Capacity and overload behavior need operational design.

## Pros and Cons of the Options

### Stateless replicated service

* Good, because Horizontal scaling
* Good, because Instance failure tolerance
* Bad, because Needs capacity management
* Bad, because Shared dependencies can bottleneck

### Single scoring instance

* Good, because Simple deployment
* Good, because No coordination
* Bad, because Single failure point
* Bad, because Limited peak capacity
