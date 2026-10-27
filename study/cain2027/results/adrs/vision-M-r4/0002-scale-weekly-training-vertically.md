# Scale weekly training vertically

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images feed a weekly retraining cycle, while infrastructure budget is tight. The brief gives no indication that training requires distributed compute.

## Decision Drivers

* Weekly retraining
* Tight infrastructure budget

## Considered Options

* Vertically scalable training (`v:3.1`)
* Distributed event computation (`v:3.3`)

## Decision Outcome

Chosen option: "Vertically scalable training" (`v:3.1`).

The brief describes periodic retraining but no scale requirement that warrants distributed infrastructure. Sources *Architecting a Scalable Real Time Learning System* and *System Architectures for Personalization and Recommendation* describe vertical scaling (s11_p06, s12_p03).

### Consequences

* Training capacity is bounded by the chosen machine.
* Revisit distribution if the image corpus outgrows that capacity.

## Pros and Cons of the Options

### Vertically scalable training

* Good, because Uses a larger single machine
* Good, because Avoids distributed setup
* Bad, because Limited by machine capacity
* Bad, because Larger machine may cost more
* Sources: `s11_p06`, `s12_p03`

### Distributed event computation

* Good, because Processes work in parallel
* Good, because Can scale across machines
* Bad, because Requires distributed infrastructure
* Bad, because Adds operational complexity
* Sources: `s02_p05`, `s04_p11`, `s12_p04`
