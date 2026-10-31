# Promote model changes through a staged release

* System: Retail demand forecasting

## Context and Problem Statement

New ideas should reach production quickly while protecting the weekly run from unproven changes.

## Decision Drivers

* Fast model iteration
* Weekly run stability
* Three-person team

## Considered Options

* Stage and validate before promotion
* Replace the production model directly

## Decision Outcome

Chosen option: "Stage and validate before promotion".

A staged release allows the team to evaluate a candidate before it becomes the weekly production model, balancing iteration speed with run stability.

### Consequences

* Keep the current production model available during validation.
* Define promotion checks and rollback steps.

## Pros and Cons of the Options

### Stage and validate before promotion

* Good, because Limits production exposure
* Good, because Supports side-by-side checks
* Bad, because Adds release steps
* Bad, because Needs acceptance criteria

### Replace the production model directly

* Good, because Few release steps
* Good, because Fastest model switch
* Bad, because Failures affect weekly run
* Bad, because Harder to compare outcomes
