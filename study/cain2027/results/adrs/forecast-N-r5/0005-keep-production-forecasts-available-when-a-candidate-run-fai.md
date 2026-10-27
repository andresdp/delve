# Keep production forecasts available when a candidate run fails

* System: Retail demand forecasting

## Context and Problem Statement

The weekly run must not be broken by new model ideas. A failure-safe release path lets experimentation proceed while preserving the most recent usable production forecasts.

## Decision Drivers

* Protect weekly run
* Fast model iteration

## Considered Options

* Publish only after a complete successful run
* Replace outputs as each stage completes

## Decision Outcome

Chosen option: "Publish only after a complete successful run".

Staging publication until the run succeeds protects consumers from incomplete results; retaining the last successful output provides continuity.

### Consequences

* Publication needs an atomic or staged handoff.
* The system retains the last successful forecast set.

## Pros and Cons of the Options

### Publish only after a complete successful run

* Good, because Avoids partial outputs
* Good, because Clear release point
* Bad, because Fresh forecasts may be delayed
* Bad, because Needs previous output retention

### Replace outputs as each stage completes

* Good, because Partial progress visible
* Good, because Less release staging
* Bad, because Can expose inconsistent results
* Bad, because Failure may erase usable output
