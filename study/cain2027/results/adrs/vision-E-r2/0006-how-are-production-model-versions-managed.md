# How are production model versions managed?

* System: On-device visual inspection

## Context and Problem Statement

Weekly updates can introduce regressions on the production line. The design space includes rollback and multiple-version deployment choices (d:10).

## Decision Drivers

* Reliable inspection
* Weekly updates
* Device fleet

## Considered Options

* Rollback to previous model version (`v:10.2`)
* N versions in production (`v:10.1`)

## Decision Outcome

Chosen option: "Rollback to previous model version" (`v:10.2`).

Keeping a rollback path provides a practical recovery option for weekly releases without requiring multiple simultaneous production versions (d:10, v:10.2).

### Consequences

* Retain the previous known-good model package.
* Define how devices receive and apply rollback instructions.

## Pros and Cons of the Options

### Rollback to previous model version

* Good, because Recovery path for regressions
* Good, because Keeps deployment simple
* Bad, because Requires retaining prior package
* Bad, because Rollback needs device coordination
* Sources: `d:10`, `v:10.2`

### N versions in production

* Good, because Supports parallel versions
* Good, because Allows staged comparison
* Bad, because More fleet complexity
* Bad, because Higher operational overhead
* Sources: `d:10`, `v:10.1`
