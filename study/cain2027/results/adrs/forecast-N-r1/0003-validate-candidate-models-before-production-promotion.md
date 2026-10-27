# Validate candidate models before production promotion

* System: Retail demand forecasting

## Context and Problem Statement

The team wants to move new model ideas to production quickly without breaking the weekly run, so experimentation needs a controlled path to production.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Three-person team

## Considered Options

* Validate candidates in an isolated promotion path
* Replace the production model directly

## Decision Outcome

Chosen option: "Validate candidates in an isolated promotion path".

A separate candidate validation and promotion path balances iteration speed with protection of the scheduled run.

### Consequences

* The promotion gate and rollback procedure need definition.
* Candidate evaluation adds work to the pipeline.

## Pros and Cons of the Options

### Validate candidates in an isolated promotion path

* Good, because Limits weekly-run disruption
* Good, because Enables candidate comparison
* Bad, because Requires validation workflow
* Bad, because Adds promotion steps

### Replace the production model directly

* Good, because Few process steps
* Good, because Fastest initial switch
* Bad, because Can disrupt weekly run
* Bad, because Harder to compare safely
