# Use vertically scalable training initially

* System: On-device visual inspection

## Context and Problem Statement

The system retrains weekly, while the team and infrastructure budget are both small.

## Decision Drivers

* Weekly training
* Tight budget
* Small team

## Considered Options

* Vertically scalable training (`v:3.1`)
* Horizontal and vertical training scalability (`v:3.2`)

## Decision Outcome

Chosen option: "Vertically scalable training" (`v:3.1`).

A larger single training machine is a simpler starting point under the stated team and budget constraints. The design point returned no attested sources for this combination, so this is a brief-driven choice rather than an established combination in the design space.

### Consequences

* Revisit distributed training if weekly jobs outgrow one machine.

## Pros and Cons of the Options

### Vertically scalable training

* Good, because Simpler operations
* Good, because Scale one machine
* Bad, because Machine capacity ceiling
* Sources: `s11_p06`, `s12_p03`

### Horizontal and vertical training scalability

* Good, because Broader scaling options
* Bad, because More infrastructure overhead
* Sources: `s02_p01`, `s15_p04`
