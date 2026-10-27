# Keep inference independent of network services

* System: On-device visual inspection

## Context and Problem Statement

Production cameras may have no network access. Inspection must therefore not depend on remote model calls or other online services during operation.

## Decision Drivers

* Often offline
* Continuous line operation

## Considered Options

* Self-contained local inference
* Remote inference service

## Decision Outcome

Chosen option: "Self-contained local inference".

Keeping inference local preserves inspection during connectivity loss, directly matching the stated deployment environment.

### Consequences

* Devices need locally available models and runtime.
* Remote monitoring cannot be assumed during outages.

## Pros and Cons of the Options

### Self-contained local inference

* Good, because Operates offline
* Good, because Predictable availability
* Bad, because Local maintenance required
* Bad, because Limited central visibility

### Remote inference service

* Good, because Centralized service updates
* Good, because Shared compute
* Bad, because Network dependency
* Bad, because Unavailable during outages
