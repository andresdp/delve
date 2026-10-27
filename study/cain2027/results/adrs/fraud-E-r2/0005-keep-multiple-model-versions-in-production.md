# Keep multiple model versions in production

* System: Card-fraud scoring service

## Context and Problem Statement

Scores must be attributable to the exact model version used. Keeping multiple versions available supports explicit version identification during rollout and operation.

## Decision Drivers

* Version traceability
* Continuous availability

## Considered Options

* N versions in production (`v:10.1`)
* Single model in production (`v:10.3`)

## Decision Outcome

Chosen option: "N versions in production" (`v:10.1`).

Concurrent versions make the version behind each score explicit while supporting model changes. The brief does not specify traffic allocation or rollout policy.

### Consequences

* Tag every score with its model version.
* Manage routing and lifecycle for active versions.

## Pros and Cons of the Options

### N versions in production

* Good, because Multiple versions available
* Good, because Supports controlled rollout
* Bad, because More serving complexity
* Bad, because Version routing required
* Sources: `d:10`, `v:10.1`

### Single model in production

* Good, because Simpler routing
* Good, because One active version
* Bad, because No concurrent versions
* Bad, because Replacement risk
* Sources: `d:10`, `v:10.3`
