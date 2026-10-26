# Validated structured output

*How should classification output be constrained?*

* System: Large-scale document classification

## Context and Problem Statement

The classifier assigns documents to claim types, so results need to fit the insurer’s classification scheme and be usable by downstream teams.

## Decision Drivers

* claim types
* multiple consumers

## Considered Options

* Free-form model response
* Validated structured output

## Decision Outcome

Chosen option: "Validated structured output".

Validating output against a defined claim-type schema makes results more consistent for downstream consumers.

### Consequences

* A taxonomy change requires schema coordination.
* Invalid outputs need a retry or exception path.

## Pros and Cons of the Options

### Free-form model response

* Good, because flexible output
* Good, because simple prompt
* Bad, because inconsistent labels
* Bad, because hard to validate

### Validated structured output

* Good, because consistent labels
* Good, because machine-checkable
* Bad, because taxonomy updates needed
* Bad, because invalid outputs need handling
