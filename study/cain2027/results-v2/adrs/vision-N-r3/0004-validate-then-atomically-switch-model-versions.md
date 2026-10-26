# Validate, then atomically switch model versions

*How should a device activate a received model?*

* System: On-device visual inspection

## Context and Problem Statement

A weekly model package can arrive when a device reconnects, but inference must remain available during and after installation.

## Decision Drivers

* Offline availability
* Reproducibility
* Weekly freshness

## Considered Options

* Validate, then atomically switch model versions
* Overwrite the active model in place

## Decision Outcome

Chosen option: "Validate, then atomically switch model versions".

Offline availability decides the choice: the current model can continue serving inspection while the new package is checked. This gives up some update speed for safer activation.

### Consequences

* Retain the previous model until the replacement is validated.
* Record which version is active after each switch.

## Pros and Cons of the Options

### Validate, then atomically switch model versions

* Good, because Offline availability: current model stays active during install
* Good, because Reproducibility: activation uses a discrete version
* Bad, because Weekly freshness: validation adds update steps

### Overwrite the active model in place

* Good, because Weekly freshness: simple direct replacement
* Bad, because Offline availability: interrupted install can disrupt inference
* Bad, because Reproducibility: partial state is harder to identify
